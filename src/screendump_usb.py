import time
import sys
import serial
import scpi
from pylibftdi import Device, USB_PID_LIST, USB_VID_LIST

USB_PID_LIST.append(0xED72);



outfile=sys.argv[2]

print("Output to "+outfile)
#exit
# configure the serial connections (the parameters differs from device to 
# device you are connecting to)
#ser = serial.Serial(
#	port=portname,
#	baudrate=115200,
#	parity=serial.PARITY_NONE,
#	stopbits=serial.STOPBITS_ONE,
#	bytesize=serial.EIGHTBITS
#)
ser = Device(mode='b')
oszi=scpi.SCPI(ser);

# Test if slave device is supported
if (oszi.device_id().find("HAMEG,HM2008")>=0):
	oszi.set_param_and_check(":HCOP:FORM", "BMP");
	screen = oszi.query_block(':HCOP:DATA?', 20)
else:	
	print("Unknown device: "+oszi.device_id())
	exit()

# Write data we got to file
f = open(outfile, 'w')
f.write(screen)
f.close

