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
from insulaudit.clmm import CarelinkUsb, Reply, ACK
from insulaudit import lib

logging.basicConfig( stream=sys.stdout )
log = logging.getLogger( 'carelink' )
log.setLevel( logging.FATAL )
log.info( 'hello world' )
io  = logging.getLogger( 'carelink.io' )
io.setLevel( logging.DEBUG )

example = '\x01U\x00\x00\x02\x00\x00\x00\x05\x04\x00mLink II\x01\x10\x02\x00\x01\x01\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

"""


'\x01U\x00\x00\x02\x00\x00\x00\x05\x04\x00mLink II\x01\x10\x02\x00\x01\x01\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'


\x01
U
\x00

\x00
\x02\x00\x00\x00\x05\x04\x00mLink II\x01\x10\x02\x00\x01\x01\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00

"""

ERROR_LOOKUP = [ "NO ERROR",
  "CRC MISMATCH",
  "COMMAND DATA ERROR",
  "COMM BUSY AND/OR COMMAND CANNOT BE EXECUTED",
  "COMMAND NOT SUPPORTED" ]

class StickStatusStruct( object ):
  statmap = {
      'receiving.complete'      : 0x01,
      'receiving.progress'      : 0x02,
      'transmit.progress'       : 0x04,
      'interface.error'         : 0x08,
      'error.receiving.overflow': 0x10,
      'error.transmit.overflow' : 0x20
  }
  value = '????'
  flags = { }
  def __init__( self, status ):
    self.raw  = status
    flags = { }
    for k,v in self.statmap.iteritems( ):
      flags[ k ] = status & v
      if status & v > 0:
        flags[ k ] = True
        self.value = status & v
    self.flags = flags

  def __str__( self ):
    return '%s:%r' %( self.__class__.__name__, self.flags )

  def __repr__( self ):
    return '<{agent}:raw={raw}:flags={flags}>'.format(
                raw   = self.raw,
                flags = self.flags,
                agent = self.__class__.__name__ )



class USBStatus( Command ):
  """
  """
  code  = [ 3 ]
  ACK   = 85  # U
  NAK   = 102 # f
  label = 'usb.status'
  __info__ = { 'error.fatal'     : 0x00
             , 'status'          : 0x00
             , 'rfBytesAvailable': 0x00
             }

  def rfByteCount( self, count ):
    return lib.BangInt( count )

  def onACK(self):
    """Called by decode on success."""
    reply = self.reply
    info = { 'error.fatal'     : reply.body[ 3 ]
           , 'status'          : StickStatusStruct( reply.body[ 5 ] )
           , 'rfBytesAvailable': self.rfByteCount( reply.body[ 6:8 ] )
           }
    self.__dict__.update( info )
    reply.info = info
    self.info  = info
    
  def decode(self):
    """Should set self.info"""
    self.reply    = Reply( self.response )
    self.info = self.__info__
    if self.reply.ack.isACK( ):
      self.onACK()
    else:
      log.info('nonack:%s' % self.reply.ack)
    self.reply.info = self.info

  def __call__( self, port ):
    """Should read from the port as needed by the command, set, self.response,
    call self.decode, and return self.  Callers should expect self.info to be
    set."""
    #time.sleep( .2 )
    response = port.read( 0 )
    response = port.read( 0 )
    response = port.read( 64 )
    self.response = response
    self.decode( )
    log.debug( 'status reply: %r' % self.info )
    return self
   

class USBProductInfo( USBStatus ):
  """Get product info from the usb device."""
  code   = [ 4, 0, 0 ]
  SW_VER = 16
  label  = 'usb.productInfo'
  rf_table  = { 001: '868.35Mhz' ,
                000: '916.5Mhz'  ,
                255: '916.5Mhz'  }
  iface_key = { 3: 'USB',
                1: 'Paradigm RF' }

  @classmethod
  def decodeInterfaces( klass, L ):
    n, tail    = L[ 0 ], L[ 1: ]
    interfaces = [ ]
    for x in xrange( n ):
      i    = x*2
      k, v = tail[i], tail[i+1]
      interfaces.append( ( k, klass.iface_key.get( v, 'UNKNOWN'  ) ) )
    return interfaces

  def onACK(self):
    reply = self.reply
    self.info = {
      'rf.freq'          : self.rf_table.get( reply.body[ 5 ], 'UNKNOWN' )
    , 'serial'           : (reply.body[ 0:3 ],
                           str( reply.body[ 0:3 ]).encode( 'hex'  ) )
    , 'product.version'  : '{0}.{1}'.format( *reply.body[ 3:5 ] )
    , 'description'      : str( reply.body[ 06:16 ] )
    , 'software.version' : '{0}.{1}'.format( *reply.body[ 16:18 ] )
    , 'interfaces'       : self.decodeInterfaces( reply.body[ 18: ] )
    }

  

class InterfaceStats( USBStatus ):
  code          = [ 5 ]
  INTERFACE_IDX = 19
  label         = 'usb.interfaceStats'
  def onACK(self):
    b = self.reply.body
    self.reply.info = {
      'errors.crc'      : b[ 0 ]
    , 'errors.sequence' : b[ 1 ]
    , 'errors.naks'     : b[ 2 ]
    , 'errors.timeouts' : b[ 3 ]
    , 'packets.received': lib.BangLong( b[ 4: 8 ] )
    , 'packets.transmit': lib.BangLong( b[ 8:12 ] )
    }

class USBInterfaceStats( InterfaceStats ):
  code          = [ 5, 1 ]
  label         = 'usb.interfaceStats'

class RadioInterfaceStats( InterfaceStats ):
  code          = [ 5, 0 ]
  label         = 'usb.interfaceStats'

class USBSignalStrength( Command ):
  code  = [ 6, 0 ]
  label = 'usb.signalStrength'
  value = '??'

  def decode(self):
    self.info = self.response[ 0 ]
    log.info( '{0}: {1}dBm'.format( self.label, self.info ) )
    reply.info = self.info
    

  def __repr__( self ):
    return '<{agent}:code={code}, label={label} {signal}dBm>'\
           .format( code   = repr( self.code ),
                    agent  = self.__class__.__name__,
                    signal = self.info,
                    label  = self.label )

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
  print "Checking status first..."
  pprint( carelink( USBStatus(           ) ).info )
  try:
    pprint( carelink( USBStatus(           ) ).info )
    pprint( carelink( USBStatus(           ) ).info )
    pprint( carelink( USBProductInfo(      ) ).info )
    pprint( carelink( USBStatus(           ) ).info )
    pprint( carelink( USBInterfaceStats(   ) ).info )
    pprint( carelink( USBStatus(           ) ).info )
    pprint( carelink( RadioInterfaceStats( ) ).info )
    pprint( carelink( USBStatus(           ) ).info )

    sendOneCommand( carelink )
    #initRadio( carelink )
    #loopSendComand( carelink )
    #loopingRead( carelink )
  except KeyboardInterrupt:
    print "closing"
  pprint( carelink( USBStatus(           ) ).info )

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
