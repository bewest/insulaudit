#!/usr/bin/python


import user

import struct
import sys
import serial
import time
import logging
import binascii
import itertools
from binascii import b2a_hex as dehex
from pprint import pprint, pformat

from insulaudit.core import Command
from insulaudit.clmm.usbstick import *
from insulaudit import lib

logging.basicConfig( stream=sys.stdout )
log = logging.getLogger( 'carelink' )
log.setLevel( logging.FATAL )
log.info( 'hello world' )
io  = logging.getLogger( 'carelink.io' )
io.setLevel( logging.DEBUG )



# RF SN
# spare serial(512): 206525
# 522: 665455
def FormatCommand( serial='206525', command=141, params=[ ] ):
  """"
 00    [ 1
 01    , 0
 02    , 167
 03    , 1
 04    , serial[ 0 ]
 05    , serial[ 1 ]
 06    , serial[ 3 ]
 07    , 0x80 | HighByte( paramCount )
 08    , LowByte( paramCount )
 09    , code == 93 ? 85 : 0
 10    , maxRetries
 11    , pagesSent > 1 ? 2 : pagesSent
 12    , 0
 14    , code
 15    , CRC8( code[ :15 ] )
 16    , command parameters....
 ??    , CRC8( command parameters )
       ]
  """

  readable = 0
  code = [ 1 , 0 , 167 , 1 ] 
  code.extend( list( bytearray( serial.encode( 'hex' ) ) ) )
  code.extend( [ 0x80 | lib.HighByte( len( params ) )
         , lib.LowByte( len( params ) )
         , command == 93 and 85 or 0
         , 2
         , 1
         , 0
         , command
         ] )
  io.info( 'crc stuff' )
  io.info( code )
  io.info( lib.hexdump( bytearray( code ) ) )
  code.append( lib.CRC8.compute( code ) )
  code.append( 0 )
  code.append( 0 )
  code.append( lib.CRC8.compute( [ 0 ] ) )
  return bytearray( code )
  

class USBReadData( Command ):
  # XXX: !!!!
  code  = [ 12, 0 ]
  label = 'usb.readdata'
  def __init__( self, length ):
    super( type( self ), self ).__init__( )
    code  = [ 12, 0 ]
    self.length = length
    self.code.extend( [ lib.HighByte( length )
                      , lib.LowByte( length ) ] )
    self.code.append( lib.CRC8.compute( self.code ) )

def readBytes( carelink, length ):
    remaining = length
    io.info( 'readBytes requested: %s' % length )
    result    = [ ]
    
    pages = int( remaining/64 ) + 1
    #while remaining > 0:
    for page in xrange( pages ):
      io.info( 'reading page:%s/%s' % ( page, pages ) )
      response  = carelink.radio( 64 )
      remaining = remaining - len( response )
      result.append( response )
      io.info( 'page:%s:len:%s' % ( page, len( response ) ) )
    result = bytearray( ).join( result )
    io.info( 'readBytes read: %s' % len( result ) )
    return result
  

def getBytesAvailable( carelink ):
  info   = carelink( USBStatus( ) ).info
  length = info[ 'rfBytesAvailable' ]
  io.info( 'initial bytes available: %s' % length )
  for x in itertools.takewhile( lambda x: length==0
                              , itertools.count( ) ):
    status = carelink( USBStatus( ) )
    length = status.info[ 'rfBytesAvailable' ]
    io.info( 'x:%s len: %s' % ( x, length ) )
    if length == 0 and x > 10:
      io.warning( 'page boundary offset problem? offset by:%s' % '?' )

  return length


# utils
def initRadio( carelink ):
  print "READ AND EMPTY RADIO"
  length = getBytesAvailable( carelink )
  print 'found length %s' % length
  response = readBytes( carelink, length )
  print 'contents of radio:'
  debug_response( response )
  pprint( carelink( USBProductInfo(      ) ).info )
  pprint( carelink( USBSignalStrength(      ) ).info )

def sendOneCommand( carelink, command=141 ):
  print '######### Send one Command ###########'
                            
  print '###### Write Command to Port #####'
  #command = FormatCommand( )
  command = FormatCommand( command=command )
  #print lib.hexdump( bytearray( command ) )
  carelink.write( str( bytearray( command ) ) )
  response = carelink.read( 64 )
  #print "### Read follows write ####"
  #print lib.hexdump( bytearray( response ) )
  response = bytearray( response )
  debug_response( response )
  return response

def debug_response( response ):
  header, body = response[ :14 ], response[ 14 : 14+response[13] ]
  print "HEADER"
  print "readable 1 == %s" % header[ 0 ]
  print "success (U) fail (f) == %s (%s)" % ( chr( header[ 1 ] ),
                                                   header[ 1 ] )
  print "error code 0 == %s" % header[ 2 ]
  print "message length: %s" % header[ 13 ]
  print lib.hexdump( header )
  print "msg"
  print lib.hexdump( body )
  print "msg: %s" % ( str( body ) )


def decodeSerial( serial ):
  return serial.encode( 'hex' )
  
def loopSendComand( carelink ):
  for x in itertools.count( ):
    print '######### BEGIN LOOP ###########'
    print 'loop:%s' % x
    sendOneCommand( carelink )



def loopingRead( carelink ):
  for x in itertools.count( ):
    print '######### BEGIN LOOP ###########'
    print 'loop:%s' % x
    length = getBytesAvailable( carelink )
    print 'found length %s' % length
    response = readBytes( carelink, length )
    print lib.hexdump( response )
    print "Read a total of %s bytes / %s requested" % ( len( response), length )
    if len( response ) < length:
      remaining = length - len( response )
      print "Response was less than requested... "
      print "trying the remainder: %s" % remaining
      response = readBytes( carelink, remaining + ( remaining % 64 ) )
    pprint( carelink( USBStatus( ) ).info )
    print 'finishing loop:%s' % x
    print '######### STATS ###########'
    print 'signal strength: %sdBm' % \
           carelink( USBSignalStrength( ) ).info
    pprint( carelink( RadioInterfaceStats( ) ).info )
    pprint( carelink( USBInterfaceStats(   ) ).info )
    pprint( carelink( USBProductInfo(      ) ).info )
    pprint( carelink( USBStatus(           ) ).info )
    print 




if __name__ == '__main__':
  print 'hello world'
  
  port = sys.argv[ 1 ]
  #port = '/dev/ttyUSB1'
  
  carelink = CarelinkUsb( port )
  try:
    try:
      pprint( carelink( USBProductInfo(      ) ).info )
      pprint( carelink( USBSignalStrength(   ) ).info )
      pprint( carelink( USBSignalStrength(   ) ).info )
      pprint( carelink( RadioInterfaceStats( ) ).info )
      pprint( carelink( USBInterfaceStats(   ) ).info )
      pprint( carelink( USBProductInfo(      ) ).info )
      pprint( carelink( USBSignalStrength(   ) ).info )
      pprint( carelink( USBStatus(           ) ).info )
      pprint( carelink( USBStatus(           ) ).info )
      pprint( carelink( USBStatus(           ) ).info )
      pprint( carelink( USBStatus(           ) ).info )

      #sendOneCommand( carelink )
      #initRadio( carelink )
      #loopSendComand( carelink )
      #loopingRead( carelink )
    except KeyboardInterrupt:
      print "closing"

  except Exception:
    carelink.close( )
    raise
  print "closing for real now"
  carelink.close( )
  sys.exit( 0 )

  pprint( carelink( USBStatus(           ) ).info )

  info   = carelink( USBStatus( ) ).info
  pprint( info )
  length = info[ 'rfBytesAvailable' ]
  print carelink.radio( 64 )
  pprint( carelink( USBStatus(           ) ).info )
  pprint( carelink( USBInterfaceStats(   ) ).info )
  pprint( carelink( RadioInterfaceStats( ) ).info )
  pprint( carelink( USBInterfaceStats(   ) ).info )
  pprint( carelink( USBProductInfo(      ) ).info )
  pprint( carelink( USBStatus(           ) ).info )
  pprint( carelink( USBProductInfo(      ) ).info )
  pprint( carelink( USBInterfaceStats(   ) ).info )
  pprint( carelink( RadioInterfaceStats( ) ).info )

    


  #print carelink( USBSignalStrength( ) )
  #print carelink( USBInterfaceStats( ) )
  #print carelink( RadioInterfaceStats( ) )
  #print carelink( USBInterfaceStats( ) )
  #print carelink( USBReadData( timeout = 2 ) )




#####
# EOF
