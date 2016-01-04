import time
import sys
import serial
import scpi
from pylibftdi import Device, USB_PID_LIST, USB_VID_LIST

# Make pylibftdi accept the HAMEG PID
USB_PID_LIST.append(0xED72);

#ser = serial.Serial(
#        port="/dev/tty.usbserial-00102126",
#        baudrate=115200,
#        parity=serial.PARITY_NONE,
#        stopbits=serial.STOPBITS_ONE,
#        bytesize=serial.EIGHTBITS
#)            

ser = Device(mode='t')
oszi=scpi.SCPI(ser) 
if (oszi.device_id().find("HAMEG,HM 2008")>=0):
    # Try to read data in binary and convert it to a csv file.
    oszi.set_param_and_check(":TRAC:SOUR", "CH1")
    oszi.set_param_and_check(":TRAC:FORM", "BYTE")

    # Get scaling factors.
    xinc=float(scpi.query(":TRACe:XINCrement?"))
    yinc=float(scpi.query(":TRACe:YINCrement?"))

    # Get offset values.
    yorig=float(scpi.query(":TRACe:YORigin?"))
    yref=float(scpi.query(":TRACe:YREFerence?"))

    # Fetch data from scope
    rawcurve=scpi.query(":TRACe:DATA?")

    for i in range(0,len(rawcurve)):
        # Calculate actual value
	floatcurve[i]=( float(rawcurve[i])-yref )*yref + yorig 

    # Try outputting data 
    for i in range(0,len(floatcurve)):
        print floatcurve[i]

#if ( oszi.device_id() != "HAMEG,HM2008,059670040,HW10060002,SW05.507-02.016" ) then:
#       exit
oszi.set_param_and_check(":TRAC:SOUR", "CH1");
oszi.set_param_and_check(":TRAC:FORM", "CSV");
#oszi.set_param_and_check(":TRAC:POIN", "MAX");

print oszi.query(":TRAC:DATA?",5);
print oszi.read(1000000, 2);

