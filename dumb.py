#!/usr/bin/python

import serial
import os, sys
import logging
import time
from insulaudit import lib
logging.basicConfig( )
log = logging.getLogger('dumb')
log.setLevel(logging.INFO)
log.info("hello world")

stage1 = bytearray( [ 0x11, 0x0D, 0x44, 0x4D, 0x53, 0x0D, 0x0D ] )

weird  = [ 0xFE ] * 14
tail   = [ 0xFF ] * 3

def send_command(port, comm):
  log.info("sending:")
  log.info(lib.hexdump(bytearray(comm)))
  port.write(str(comm))
  time.sleep(.2)
  response = ''.join(port.readlines( ))
  if len(response) > 0:
    print "RESPONSE!!!!"
    print lib.hexdump(bytearray(response))
  return response
  
  

def main(device):
  log.info( "opening device: %s" % device )
  ser = serial.Serial(device)
  ser.setTimeout(5)
  send_command(ser, stage1)
  send_command(ser, stage1)
  send_command(ser, bytearray( weird + tail ) )
  send_command(ser, bytearray( weird + tail ) )
  ser.close( )


if __name__ == '__main__':
  main(sys.argv[1])
#####
# EOF
