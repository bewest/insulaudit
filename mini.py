#!/usr/bin/python

import serial
from pprint import pprint, pformat

import insulaudit
from insulaudit.log import io
from insulaudit.devices import lsultramini

PORT = '/dev/ttyUSB0'

def format_packet( command ):
  COMMAND = [
    2,  # STX
    len( command ) + 6 ] # mundane details are always 6 bytes
  pass

def read_serial( ):
  commands = [ 5, 11, 2, 0, 0, 0, 0, 132, 106, 232, 115, 0 ]

def get_serial( port, timeout=2 ):
  return serial.Serial( port, timeout=timeout )

def init( ):
  mini = lsultramini.LSUltraMini( PORT, 0.5 )
  print "is open? %s\n timeout: %s" % ( mini.serial.isOpen( ), mini.serial.getTimeout() )
  mini.disconnect( )
  print "Initial DISCONNECT"
  print "GETTING FIRMWARE INFO"
  firmware = mini.execute( lsultramini.DiscoverFirmware( ) )
  print "FIRMWARE IS: %s" % firmware 
  return mini



if __name__ == '__main__':
  port = init()
  io.info( port )

