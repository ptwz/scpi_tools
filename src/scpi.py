import time
import sys
import serial
from pylibftdi import Device, USB_PID_LIST, USB_VID_LIST


"""
This class implements SCPI compliant communincation routines
currently intended for use with e.g. oscilloscopes.
As of now, only RS-232 and HAMEG USB links are supported, maybe this class 
will support GPIB and other means of comm. as well.
"""
class SCPI:
    def flush(self):
        if ( type(self.__ser) is serial.Serial ):
            self.__ser.flushOutput()
            self.__ser.flushInput()
        if (type(self.__ser) is Device):
            self.__ser.flush()

    def read(self, length, timeout=1):
        """
        Read data from the serial device, using timeouts.
        Timeout is given in seconds 
        """
        if ( type(self.__ser) is serial.Serial):
            oldtimeout=self.__ser.timeout
            self.__ser.timeout=timeout
            r = self.__ser.read(length)
            self.__ser.timeout=oldtimeout
        if (type(self.__ser) is Device):
            endtime = timeout + time.time() 
            r = ""
            curtime = 0
            while ( ( len(r) < length ) and ( curtime < endtime) ):
                curtime = time.time() 
                r = r + self.__ser.read(length-len(r))
        return(r)

    def readline(self, timeout=1):
        """
        Read a line from the serial port
        Timeout is given in seconds 
        """
        if ( type(self.__ser) is serial.Serial):
            oldtimeout=self.__ser.timeout
            self.__ser.timeout=timeout
            r = self.__ser.readline()
            self.__ser.timeout=oldtimeout
        if (type(self.__ser) is Device):
            endtime = timeout + time.time() 
            r = ""
            curtime = 0
            while ( not ('\n' in r  or '\r' in r ) and ( curtime < endtime) ):
                curtime = time.time() 
                r = r + self.__ser.read(1)
        return(r)

    def write(self, string):
        self.__ser.write(string);

    def send_cmd(self, cmd):
        """
        Sends SCPI command.

        Serial i/o buffers will be cleared before doing so to avoid 
        confusion

        param cmd  Command to be sent out to device, without 
                 termination chars

        note This function will _not_ do any response processing!
        """
        self.flush()
        self.__ser.write(cmd+ '\r\n')

    def query(self, cmd, timeout):
        """
        Sends an SCPI query and tries to parse resulting data.

        This function sends the literal passed as cmd to the device
        and waits for it to answer. Each part of the answer is expected
        to arrive within of given timeout after last send or receive operation

        It will also try to repeat a transmission if a block-transfer fails 
        or times out before having read all the expected data
        """
        self.send_cmd(";");
        self.send_cmd(cmd)
        # Read first byte and deduce format of answer.
        answer = self.__ser.read(1)
        # If it does not start with "#", expect just one line.
        if (answer != "#"):
            answer = answer + self.readline()
            answer = answer.rstrip('\r\n ');
            return(answer)
        else:
            # Now there may be either a format specifier or a
            # length identifier.
            answer = self.__ser.read(1)
            if ( answer.isdigit() ):
                # If it is numeric its the amount of ascii numbers
                # to follow wich make up the binary blocks length.
                length = int(self.__ser.read(int(answer)))
                print "Will read "+str(length)+" bytes from device"
                answer = self.__ser.read(length)
                if (len(answer)<length):
                    print "Did not receive all data, retrying"
                    return query(cmd, timeout)
                return(answer)
            # If answer did not start with a numeral, try to decode 
            # initial byte header and read rest of line as ascii.
            data=self.readline()
            if (answer == 'B' ):
                return(int(data, 1))
            if (answer == 'Q' ):
                return(int(data, 7))
            if (answer == 'H' ):
                return(int(data, 16))
            # Default:
            print ("Don't know how to handle type '#"+answer+
                  "'. Might return garbage.")
            return(answer+data)
    
    def query_string(self, cmd, timeout):
        """
        Sends an SCPI command and reads texutal reply form device
        
        param timeout -1 infinite, otherwise real in seconds.
        """
        self.send_cmd(cmd)
        answer = ""
        answer = self.readline(timeout)
        answer = answer.rstrip('\r\n ');
        return answer

    def query_block(self, cmd, timeout):
        """
        Send an SCPI query and read BLOCK-format data. 

        param cmd     Command/Query to be executed
        param timeout Numer of seconds until timeout
        """
        self.send_cmd(cmd)
        out = ' ';
        while out != '#':
            # Answer should start with '#' sign.
            out=self.read(1)
            print out
        # Next should be an ASCII written number.
        out=self.read(1)
        length=int(out)
        if length <= 0:
            print "No ASCII length data?! Read |",out,"| made length=",length
            return -2
        # Now read actual number of bytes to follow.
        out=self.read(length)
        length=int(out)
        if length <= 0:
            print "No Data?!"
        print "Will read "+str(length)+" bytes from scope!"
        block = self.read(length)
        if (len(block)<length):
            print "Only read "+str(len(block))+". Retrying..."
            block=query_block(self, cmd, timeout)

        return(block);
        
    def set_param_and_check(self, param, value):
        """
        Sends a given parameter to the device and tries to read
        it back to make sure it arrived correctly.
        
        param param  Parameter to modify
        param value  Value to set
        return 0 on success, -1 on error
        """
        # Send set command
        setcmd=param+" "+value+";"
        self.send_cmd(setcmd)
        time.sleep(.250)
        # Read back actual value
        getcmd=param+"?"
        answer=self.query_string(getcmd, 1);
        # If setting parameter was successful, return 0
        # return -1 otherwise.
        if (answer != value):
            print ("Tried to set "+param+" to '"+value+"' but got '"+answer+ 
                  "' instead.\n")
            return -1
        else:
            return 0
    
    def __init__(self, port, baud=115200):
        """
        Initializes SCPI slave device from a given port.

        Port can either be an already initialized pyserial port
        or may be a string, specifiying the port to be used.
        Special name: hamegusb, this uses the HM2008 USB interface
        """
        if ( type(port) is str):
            if (port == "hamegusb"):
                USB_PID_LIST.append(0xED72);
                self.__ser = Device(mode='b')
            else:
        # configure the serial connections (the parameters differs from device
        # to device you are connecting to)
                self.__ser = serial.Serial(
                   port=port,
                   baudrate=baud,
                   parity=serial.PARITY_NONE,
                   stopbits=serial.STOPBITS_ONE,
                   bytesize=serial.EIGHTBITS
                )
        else:
            self.__ser = port
        # Try at least an *IDN? command, if this fails
        # most likely nothing will work on the device at all.
        self.__device_id = self.query_string("*IDN?", 1);
        print "Found >>"+self.__device_id

    def device_id(self):
        return self.__device_id;
