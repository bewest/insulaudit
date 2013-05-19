#!/usr/bin/python

import serial
import sys
from pprint import pprint, pformat

import insulaudit
from insulaudit.log import io
from insulaudit.devices import lsultramini

import argparse
import argcomplete # PYTHON_ARGCOMPLETE_OK
import dateutil

PORT = '/home/bewest/dev/vmodem0'

def format_packet( command ):
  COMMAND = [
    2,  # STX
    len( command ) + 6 ] # mundane details are always 6 bytes
  pass

def read_serial( ):
  commands = [ 5, 11, 2, 0, 0, 0, 0, 132, 106, 232, 115, 0 ]

def get_serial( port, timeout=2 ):
  return serial.Serial( port, timeout=timeout )

def init(args):
  mini = lsultramini.LSUltraMini( PORT, 0.5 )
  print "is open? %s\n timeout: %s" % ( mini.serial.isOpen( ), mini.serial.getTimeout() )
  mini.disconnect( )
  print "Initial DISCONNECT"
  print "GETTING FIRMWARE INFO"
  firmware = mini.execute( lsultramini.DiscoverFirmware( ) )
  print "FIRMWARE IS: %s" % firmware 
  print ""
  print "read serial number"
  serial = mini.execute( lsultramini.ReadSerialNumber( ) )
  print "serial number: %s" % serial 
  print ""
  print "number of available records:"
  max_records = mini.execute( lsultramini.ReadAvailableRecords( ) )
  print "max records: %s" % max_records 
  print ""
  print "all records"
  records = [ ]
  for x in xrange( max_records ):
    print 'record: %s' % x
    r = mini.execute( lsultramini.ReadGlucoseRecord(idx=x ) )
    ts, sugar = dateutil.parser.parse(r[0]), r[1]
    msg = ','.join([ts.isoformat( ), str(sugar)])
    print msg
    args.output.write(msg + "\n")
    records.append( r )

  print "total records found:%s" % len(records)

  return mini



if __name__ == '__main__':
  parser = argparse.ArgumentParser(add_help=True)
  parser.add_argument('--output', type=argparse.FileType('w'),
                      default="sugars.txt")
  parser.add_argument('port', type=str,
                      default=PORT)
  args = parser.parse_args( )
  # PORT = len(sys.argv) > 1 and sys.argv[1] or PORT
  PORT = args.port
  io.info("using PORT %s" % PORT)
  port = init(args)
  io.info( port )

