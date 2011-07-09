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


def EnablePumpRadioCmd():
  """
    Enables some kind of special multi transmit mode
  """
  cmd = FormatCommand(command=93, params=[ 0x01, 0x0A ], retries=0, expectedPages=0)
  return cmd

# RF SN
# spare serial(512): 206525
# 522: 665455
def FormatCommand( serial='665455', command=141, params=[ ], retries=2, expectedPages=1 ):
  """"
 Write Radio Buffer Commands look like this.
 While the formatting of this command seems correct, reads of usb status
 afterwards should be setting tx indicator and length fields.  Instead we're
 getting error fields.

 00    [ 0x01
 01    , 0x00
 02    , 0xA7 # 167, tx.packet
 03    , 0x01 # ?? potential sequence count?
 04    , serial[ 0 ]
 05    , serial[ 1 ]
 06    , serial[ 3 ]
 07    , 0x80 | HighByte( paramCount )
 08    , LowByte( paramCount )
 09    , code == 93 ? 85 : 0 # initialize pump rf!!!?
 10    , maxRetries # sequence count?
 11    , pagesSent > 1 ? 2 : pagesSent # sequence count?
 12    , 0
 13    , code
 14    , CRC8( code[ :15 ] )
 15    , command parameters....
 ??    , CRC8( command parameters )
       ]

 The Pump Packet looks like this:
 7 bytes with parameters on the end
 00     167
 01     serial[ 0 ]
 02     serial[ 1 ]
 03     serial[ 2 ]
 04     commandCode
 05     sequenceNumber or paramCount
 06     [ parameters ]
 06/07  CRC8(packet)

 or:
 167, serial, code, seq/param, params, CRC8(packet)
NB the whole thing is wrapped by encodeDC()

ACK: is:


  >>> FormatCommand( serial='665455', command=141 )
  bytearray( [ 0x01, 0x00, 0xA7, 0x01, 0x66, 0x54, 0x55, 0x80,
               0x00, 0x00, 0x02, 0x01, 0x00, 0x8D, 0x5B, 0x00 ] )
  """

  readable = 0
  code = [ 1 , 0 , 167 , 1, ] 
  code.extend( list( bytearray( serial.decode('hex') ) ) )
  code.extend( [ 0x80 | lib.HighByte( len( params ) )
         , lib.LowByte( len( params ) )
         , command == 93 and 85 or 0
         , retries
         , expectedPages
         , 0
         , command
         ] )
  io.info( 'crc stuff' )
  io.info( code )
  code.append( lib.CRC8.compute( code ) )
  code.extend( params )
  code.append( lib.CRC8.compute( params ) )
  io.info( '\n' + lib.hexdump( bytearray( code ) ) )
  return bytearray( code )
  

class USBRadioCommand( Command ):
  # XXX: !!!!
  code = [ 113 ]
  __reply_header__  = [ 12, 0 ]
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
  pprint( carelink( USBSignalStrength( ) ).info )
  pprint( carelink( USBProductInfo(    ) ).info )

def waitForSignal(stick):
   strength = 0
   while strength < 1:
     strength = stick( USBSignalStrength( ) ).info
     io.info( "signal strength: %sdBm" % strength )
   return strength

def getNumBytes(stick):
  io.info( '##get numbytes')
  rfBytes = 0
  usbstatus = stick( USBStatus( ) )
  
  start = time.time()
  while (rfBytes == 0 and time.time() - start < 3) \
        or usbstatus.info[ 'status' ].flags[ 'receiving.complete' ]:
    try:
      usbstatus = stick( USBStatus( ) )
      time.sleep(.1)
      rfBytes   = usbstatus.info[ 'rfBytesAvailable' ]
    except CommErrorException, e:
      io.error(e)
  print "RFBYTES: %s" % rfBytes
  return rfBytes
  

def sendOneCommand( carelink, command=141 ):
  print '######### Send one Command ###########'
  time.sleep(.1)
                            
  print '###### Write Command to Port #####'
  #command = FormatCommand( )
  command = FormatCommand( command=command )
  #print lib.hexdump( bytearray( command ) )
  carelink.write( str( bytearray( command ) ) )
  time.sleep(1.7)
  response = carelink.read( 64 )
  time.sleep(1.7)
  rfBytes = getNumBytes(carelink)

  print "RFBYTES: %s" % rfBytes
  if rfBytes > 0:
    print "read data"
    print carelink.radio( rfBytes )
  else:
    print "FAILED TO FIND BYTES"

  return
  #debug_response( response )

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
      waitForSignal(carelink)
      pprint( carelink( RadioInterfaceStats( ) ).info )
      pprint( carelink( USBInterfaceStats(   ) ).info )
      pprint( carelink( USBProductInfo(      ) ).info )
      waitForSignal(carelink)
      carelink.write( str( EnablePumpRadioCmd( ) ) )
      reply = carelink.read( 64 )
      sendOneCommand( carelink, command=0x75 )
      #sendOneCommand( carelink, command=141 )
      pprint( carelink( USBProductInfo(      ) ).info )
      pprint( carelink( RadioInterfaceStats( ) ).info )
      pprint( carelink( USBInterfaceStats(   ) ).info )
      #sendOneCommand( command=0x75, carelink )
      ######
      # pprint( carelink( USBStatus(           ) ).info )
      # pprint( carelink( USBStatus(           ) ).info )
      # pprint( carelink( USBStatus(           ) ).info )
      # pprint( carelink( USBStatus(           ) ).info )

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
