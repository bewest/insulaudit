#!/usr/bin/python



import struct
import sys
import serial
import time
import logging
import binascii
from binascii import b2a_hex as dehex
from pprint import pprint, pformat

logging.basicConfig( stream=sys.stdout )
log = logging.getLogger( 'carelink' )
log.setLevel( logging.DEBUG )
log.info( 'hello world' )

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

class Command( object ):
  """
  A code should be an array of ints.
  These are the messages we'll send to the communications device.
  """
  code        = [ 3 ]
  """
  """
  description = """This is the read status command.
  Issuing this command should result in reading a string 64 characters
  long.  The first byte should be a 1 and the second byte should be a U if
  everything is ok.
  """
  label       = 'usb ack'
  # Default timeout for a read.
  timeout     = 2
  sleep       = 1
  info        = None

  min_reply_size  = 64
  def __init__( self, **kwds ):
    self.apply_opts( **kwds )

  def apply_opts( self, **kwds ):
    for i in [ 'code', 'label', 'description', 'timeout', 'sleep' ]:
      setattr( self, i, kwds.get( i, getattr( self, i ) ) )

  def __str__( self ):
    x = str( bytearray( self.code ) )
    #s = '{label}: {msg}'.format( label=self.label, msg=self.info )
    return x

  def __repr__( self ):
    return '<{agent}:code={code}, label={label}, info={info}>'\
           .format( code  =repr( self.code ),
                    agent =self.__class__.__name__,
                    label =self.label,
                    info  =self.info )

  def __call__( self, reply, device=False ):
    self.last_reply = reply
    reply.info = self.info
    return reply

def BangInt( ints ):
  ( x, y ) = ints
  return ( x & 0xFF ) << 8 | y & 0xFF;
  

class USBStatus( Command ):
  """
  """
  code  = [ 3 ]
  ACK   = 85  # U
  NAK   = 102 # f
  label = 'usb.status'

  def rfByteCount( self, count ):
    return BangInt( count )

  def __call__( self, reply, *args ):
    info = { 'error.fatal'     : reply.body[ 3 ]
           , 'status'          : CarelinkComStatus( reply.body[ 5 ] )
           , 'rfBytesAvailable': self.rfByteCount( reply.body[ 6:8 ] )
           }
    self.__dict__.update( info )
    reply.info = info
    self.info  = info
    log.debug( 'status reply: %r' % info )
    return reply
   

class USBProductInfo( Command ):
  """Get product info from the usb device."""
  code   = [ 4 ]
  SW_VER = 16
  label  = 'usb.productInfo'
  rf_table = { 001: '868.35Mhz' ,
               255: '916.5Mhz'  }

  def __call__( self, reply, device ):
    info = {
      'rf.freq'          : self.rf_table.get( reply.body[ 5 ], 'UNKNOWN' )
    , 'serial'           : reply.body[ 0:3 ]
    , 'product.version'  : reply.body[ 3:5 ]
    , 'description'      : str( reply.body[ 06:16 ] )
    , 'software.version' : reply.body[ 16:18 ]
    , 'interfaces'       : reply.body[ 18 ]
    }
    log.info( 'usbproductinfo: %r' % info )
    self.__dict__.update( info )
    reply.info = info
    return reply

def BangLong( bytez ):
  ( a, b, c, d ) = bytez
  l = a << 24 | b << 16 | c << 8 | d;
  return l


class InterfaceStats( Command ):
  code          = [ 5 ]
  INTERFACE_IDX = 19
  label         = 'usb.interfaceStats'
  def __call__( self, reply, *args ):
    b = reply.body
    reply.info = {
      'errors.crc'      : b[ 0 ]
    , 'errors.sequence' : b[ 1 ]
    , 'errors.naks'     : b[ 2 ]
    , 'errors.timeouts' : b[ 3 ]
    , 'packets.received': BangLong( b[ 4: 8 ] )
    , 'packets.transmit': BangLong( b[ 8:12 ] )
    }
    return reply

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

  def __call__( self, reply, *args ):
    self.value = reply.body[ 0 ]
    log.info( '{0}: {1}dBm'.format( self.label, self.value ) )
    reply.info = self.value
    return reply

  def __repr__( self ):
    return '<{agent}:code={code}, label={label} {signal}dBm>'\
           .format( code   = repr( self.code ),
                    agent  = self.__class__.__name__,
                    signal = self.value,
                    label  = self.label )

class USBReadData( Command ):
  # XXX: !!!!
  code  = [ 12 ]
  label = 'usb.readdata'

class CarelinkUsb( object ):
  timeout = 0
  def __init__( self, port, timeout=timeout ):
    self.timeout = timeout
    self.open( port )


  def open( self, newPort=False ):
    if newPort:
      self.port = newPort

    self.serial = serial.Serial( self.port, timeout=self.timeout )

    if self.serial.isOpen( ):
      log.info( '{agent} opened serial port: {serial}'\
         .format( serial = repr( self.serial ),
                  agent  =self.__class__.__name__
                ) )

  def write( self, string ):
    r = self.serial.write( string )
    log.info( 'usb.write len={len}: {0}'.format( string.encode( 'string_escape' ) ,
                                                 len=len(string) ) )
    return r

  def read( self, c ):
    r = self.serial.read( c )
    log.info( 'usb.read: {0}'.format(
              str( bytearray( r ) ).encode( 'string_escape' ) ) )
    log.debug( 'usb.read.len: %s' % len( r ) )
    return r
    
  def readline( self ):
    r = self.serial.readline( )
    log.info( 'usb.readline: {0}'.format(
              str( bytearray( r ) ).encode( 'string_escape' ) ) )
    log.debug( 'usb.readline.len: %s' % len( r ) )
    return r
      
  def readlines( self ):
    r = self.serial.readlines( )
    log.info( 'usb.readlines: {0}'.format(
              str( bytearray( r ) ).encode( 'string_escape' ) ) )
    log.debug( 'usb.readlines.len: %s' % len( r ) )
    return r


  def __call__( self, command ):
    self.prevCommand = command
    x = str( command )
    self.serial.setTimeout( command.timeout )
    log.debug( 'setting timeout: %s' % command.timeout )
    self.write( x )
    log.debug( 'sent command, waiting' )
    time.sleep( command.sleep )
    response = self.read( 64 )
    # log.debug( 'response: %s' % bytearray( response ) )
    reply    = Reply( response )
    log.debug( 'command {0} inspects ACK{1}'.format(
                repr( command ),
                repr( reply.ack ) ) )
    reply    = command( reply, self )
    return reply
    

class CarelinkException( Exception ): pass

class NoReplyException( CarelinkException ): pass

class CarelinkComStatus( object ):
  statmap = {
      'receiving.complete'      : 0x01,
      'receiving.progress'      : 0x02,
      'transmit.progress'       : 0x04,
      'interface.error'         : 0x08,
      'error.receiving.overflow': 0x10,
      'error.transmit.overflow' : 0x20
  }
  name  = 'ERROR'
  value = '????'
  flags = { }
  def __init__( self, status ):
    self.raw  = status
    self.name = ''.join( [ self.name, ' ',
                         str( bytearray( [ status ] )[ 0 ] ) ] )
    flags = { }
    for k,v in self.statmap.iteritems( ):
      log.debug( 'status lookup: {0}: {1}'.format( k,v ) )
      flags[ k ] = status & v
      if status & v > 0:
        self.name  = k
        flags[ k ] = True
        self.value = status & v
    self.flags = flags

  def __str__( self ):
    return '%s:%s:%s' %( self.__class__.__name__, self.name, self.value )

  def __repr__( self ):
    return ''.join( [
          '<', '{agent}',
          ':', '{name}',
          ':', 'raw={raw}',
          ':', 'value={value}'
             , '>' ] ).format(
                raw   = self.raw,
                name  = self.name,
                value = self.value,
                agent = self.__class__.__name__
          )

class ACK( object ):
  ACK     = 85  # U
  NAK     = 102 # f
  __ack__ = 'ACK'
  def __init__( self, head ):
    ( self.power, self.error, self.code ) = head
  
  def __repr__( self ):
    return (     self.power == 1
             and self.error == self.ACK
           ) and self.__ack__  or self.__nak__( )

  def __nak__( self ):
    return ''.join( [ chr( self.error )
             , ' ', self.reason( )  ] )

  def reason( self ):
    return 'UNKNOWN REASON'
    
class Reply( object ):
  
  log    = logging.getLogger( 'reply' )
  ack    = False
  info   = None

  def __init__( self, raw_reply ):
    self.log = logging.getLogger( self.__class__.__name__ )
    self.raw = raw_reply
    self.msg = bytearray( raw_reply )
    try:
      self.ack  = ACK( self.msg[ 0:3 ] )
      self.body = self.msg[ 3: len(self.msg) - 3 ]
    except IndexError, e:
      raise NoReplyException( e )
    #self.readBytesAvailable = self.msg[ 3:4 ]
    self.printable = str( self.msg ).encode( 'string_escape' )
    log.debug( 'init reply.raw: %s' % self.printable )


  @staticmethod
  def dehex( S ):
    return [ dehex( l ) for l in S ]

  def __str__( self ):
    return pformat( { 'info' : repr( self.info )
                    , 'ack'  : self.ack
                    , 'body' : self.body } )

  def __repr__( self ):
    return "<{agent}:ack={ack}:{0}>".format( self.info,
                                   agent=self.__class__.__name__,
                                   ack=self.ack )



if __name__ == '__main__':
  print 'hello world'
  
  port = '/dev/ttyUSB1'
  
  carelink = CarelinkUsb( port )
  
  print carelink( USBStatus( ) )
  print carelink( USBProductInfo( ) )
  print carelink( USBSignalStrength( ) )
  print carelink( USBInterfaceStats( ) )
  print carelink( RadioInterfaceStats( ) )
  #print carelink( USBInterfaceStats( ) )
  #print carelink( USBReadData( timeout = 2 ) )




#####
# EOF
