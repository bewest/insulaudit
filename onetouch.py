#!/usr/bin/python

import user
import serial
from pprint import pprint, pformat

import insulaudit
from insulaudit.data import glucose
from insulaudit.log import io
from insulaudit.devices import onetouch2
import sys

import logging
logging.basicConfig( )
io.setLevel(logging.INFO)
PORT = '/dev/ttyUSB0'

def get_serial( port, timeout=2 ):
  return serial.Serial( port, timeout=timeout )

def init( ):
  mini = onetouch2.OneTouchUltra2( PORT, 5 )
  print "is open? %s\n timeout: %s" % ( mini.serial.isOpen( ), mini.serial.getTimeout() )
  print ""
  print "read serial number"
  serial = mini.execute( onetouch2.ReadSerial( ) )
  print "serial number: %s" % serial 
  print ""
  if serial == "":
    print "could not connect"
    sys.exit(1)
  print ""
  print "read firmware number"
  firmware = mini.execute( onetouch2.ReadFirmware( ) )
  print "firmware: %s" % firmware 
  print ""
  print "RFID"
  print mini.execute( onetouch2.ReadRFID( ) )
  print "GLUCOSE"
  data = mini.read_glucose( )
  print data
  print "len glucose: %s" % len( data )
  head, body = data 
  output = open( 'sugars-debug.txt', 'w' )
  output.write( glucose.format_records( body ) )
  output.write( '\n' )
  output.close( )

  return mini



if __name__ == '__main__':
  port = init()
  io.info( port )
  port.close( )

#####
# EOF
