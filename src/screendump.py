import time
import sys
import serial
import scpi

port=sys.argv[1]
outfile=sys.argv[2]

print("Device at: {}\nOutput to: ".format(port, outfile))
oszi=scpi.SCPI(port);

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

