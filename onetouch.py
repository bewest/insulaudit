#!/usr/bin/python

import serial
from pprint import pprint, pformat

import insulaudit
from insulaudit.log import io
from insulaudit.devices import onetouch2

PORT = '/dev/ttyUSB0'

def get_serial( port, timeout=2 ):
  return serial.Serial( port, timeout=timeout )

def init( ):
  mini = onetouch2.OneTouchUltra2( PORT, 0.5 )
  print "is open? %s\n timeout: %s" % ( mini.serial.isOpen( ), mini.serial.getTimeout() )
  print ""
  print "read serial number"
  serial = mini.execute( onetouch2.ReadSerial( ) )
  print "serial number: %s" % serial 
  print ""
  print ""
  print "read firmware number"
  firmware = mini.execute( onetouch2.ReadFirmware( ) )
  print "firmware: %s" % firmware 
  print ""
  print "RFID"
  print mini.execute( onetouch2.ReadRFID( ) )
  print "GLUCOSE"
  glucose = mini.read_glucose( )
  print glucose
  print "len glucose: %s" % len( glucose )
  head, body = glucose
  output = open( 'sugars-debug.txt', 'w' )
  for record in body:
    date, value = record
    output.write( '\t'.join( [ date.isoformat( ), str( value ) ] ) )
    output.write( '\n' )
  
  output.close( )

  return mini



if __name__ == '__main__':
  port = init()
  io.info( port )

