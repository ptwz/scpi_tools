import time
import sys
import serial
import scpi
from pylibftdi import Device, USB_PID_LIST, USB_VID_LIST

port=sys.argv[1]
outfile=sys.argv[2]

oszi=scpi.SCPI(port)

oszi.set_param_and_check(":TRAC:SOUR", "CH1");
oszi.set_param_and_check(":TRAC:FORM", "CSV");
#oszi.set_param_and_check(":TRAC:POIN", "MAX");

print oszi.query(":TRAC:DATA?",5);
with open(outfile, "w") as f:
    f.write(oszi.read(1000000, 2));


