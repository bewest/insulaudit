#!/usr/bin/python



import struct
import sys
import serial
import time
import logging
import binascii
import itertools
from binascii import b2a_hex as dehex
from pprint import pprint, pformat

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

  def hexdump( self ):
    return lib.hexdump( bytearray( self.code ) )

  def bytez( self ):
    return bytearray( self.code )

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
  __info__ = { 'error.fatal'     : 0x00
             , 'status'          : 0x00
             , 'rfBytesAvailable': 0x00
             }

  def rfByteCount( self, count ):
    return BangInt( count )

  def __call__( self, reply, *args ):
    self.info = self.__info__
    if reply.ack.isACK( ):
      info = { 'error.fatal'     : reply.body[ 3 ]
             , 'status'          : CarelinkComStatus( reply.body[ 5 ] )
             , 'rfBytesAvailable': self.rfByteCount( reply.body[ 6:8 ] )
             }
      self.__dict__.update( info )
      reply.info = info
      self.info  = info
    reply.info = self.info
    log.debug( 'status reply: %r' % self.info )
    return reply
   

class USBProductInfo( Command ):
  """Get product info from the usb device."""
  code   = [ 4 ]
  SW_VER = 16
  label  = 'usb.productInfo'
  rf_table  = { 001: '868.35Mhz' ,
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

  def __call__( self, reply, device ):
    info = {
      'rf.freq'          : self.rf_table.get( reply.body[ 5 ], 'UNKNOWN' )
    , 'serial'           : sum( reply.body[ 0:3 ] )
    , 'product.version'  : '{0}.{1}'.format( *reply.body[ 3:5 ] )
    , 'description'      : str( reply.body[ 06:16 ] )
    , 'software.version' : '{0}.{1}'.format( *reply.body[ 16:18 ] )
    , 'interfaces'       : self.decodeInterfaces( reply.body[ 18: ] )
    }
    log.info( 'usbproductinfo: %r' % info )
    self.__dict__.update( info )
    reply.info    = info
    reply.command = self
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

class lib:

  @staticmethod
  def hexdump( src, length=8 ):
    if len( src ) == 0:
      return ''
    result = [ ]
    digits = 4 if isinstance( src, unicode ) else 2
    for i in xrange( 0, len( src ), length ):
      s    = src[i:i+length]
      hexa = ' '.join( [ '%#04x' %  x for x in list( s ) ] )
      text = ''.join( [ chr(x) if 0x20 <= x < 0x7F else '.' \
                      for x in s ] )
      #b'' .join( [ x if 0x20 <= x < 0x7F else b'.' \
      #                      for x in s ] )
      #''.join( [ chr(x) if 0x20 <=  x < 0x7F else '.' x \
      #            for x in s ] )
      result.append( "%04X   %-*s   %s" % \
                   ( i, length * ( digits + 1 )
                   , hexa, text ) )
    return '\n'.join(result)


  @staticmethod
  def HighByte( arg ):
    # may not be correct. java uses an unsigned shift: >>>
    return arg >> 8 & 0xFF

  @staticmethod
  def LowByte( arg ):
    return arg & 0xFF
  class CRC8:
    lookup = [ 0, 155, 173, 54, 193, 90, 108, 247, 25, 130, 180, 47,
      216, 67, 117, 238, 50, 169, 159, 4, 243, 104, 94, 197, 43, 176,
      134, 29, 234, 113, 71, 220, 100, 255, 201, 82, 165, 62, 8, 147,
      125, 230, 208, 75, 188, 39, 17, 138, 86, 205, 251, 96, 151, 12,
      58, 161, 79, 212, 226, 121, 142, 21, 35, 184, 200, 83, 101, 254,
      9, 146, 164, 63, 209, 74, 124, 231, 16, 139, 189, 38, 250, 97,
      87, 204, 59, 160, 150, 13, 227, 120, 78, 213, 34, 185, 143, 20,
      172, 55, 1, 154, 109, 246, 192, 91, 181, 46, 24, 131, 116, 239,
      217, 66, 158, 5, 51, 168, 95, 196, 242, 105, 135, 28, 42, 177,
      70, 221, 235, 112, 11, 144, 166, 61, 202, 81, 103, 252, 18, 137,
      191, 36, 211, 72, 126, 229, 57, 162, 148, 15, 248, 99, 85, 206,
      32, 187, 141, 22, 225, 122, 76, 215, 111, 244, 194, 89, 174, 53,
      3, 152, 118, 237, 219, 64, 183, 44, 26, 129, 93, 198, 240, 107,
      156, 7, 49, 170, 68, 223, 233, 114, 133, 30, 40, 179, 195, 88,
      110, 245, 2, 153, 175, 52, 218, 65, 119, 236, 27, 128, 182, 45,
      241, 106, 92, 199, 48, 171, 157, 6, 232, 115, 69, 222, 41, 178,
      132, 31, 167, 60, 10, 145, 102, 253, 203, 80, 190, 37, 19, 136,
      127, 228, 210, 73, 149, 14, 56, 163, 84, 207, 249, 98, 140, 23,
      33, 186, 77, 214, 224, 123 ]

    @classmethod
    def compute( klass, block ):
      result = 0
      for i in xrange( len( block ) ):
        result = klass.lookup[ ( result ^ block[ i ] & 0xFF ) ]
      return result

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


class CarelinkUsb( object ):
  class ID:
    VENDOR  = 0x0a21
    PRODUCT = 0x8001
  timeout = .150
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

  def close( self ):
    io.info( 'closing serial port' )
    return self.serial.close( )

  def radio( self, length, crc=True ):
    code = [ 12, 0 ]
    if crc:
      code.extend( [ lib.HighByte( length )
                   , lib.LowByte( length  ) ] )
      code.append( lib.CRC8.compute( code ) )
    self.write( str( bytearray( code ) ) )
    time.sleep( 0.200 )
    return bytearray( self.read( 64 ) )
    
  def write( self, string ):
    r = self.serial.write( string )
    io.info( 'usb.write.len: %s\n%s' % ( len( string ),
                                         lib.hexdump( bytearray( string ) ) ) )
    return r

  def read( self, c ):
    r = self.serial.read( c )
    io.info( 'usb.read.len: %s'   % ( len( r ) ) )
    io.info( 'usb.read.raw: \n%s' % ( lib.hexdump( bytearray( r ) ) ) )
    return r
    
  def readline( self ):
    r = self.serial.readline( )
    io.info( 'usb.read.len: %s\n%s' % ( len( r ),
                                          lib.hexdump( r ) ) )
    return r
      
  def readlines( self ):
    r = self.serial.readlines( )
    io.info( 'usb.read.len: %s\n%s' % ( len( r ),
                                          lib.hexdump( r ) ) )
    return r


  def __call__( self, command ):
    self.prevCommand = command
    x = str( command )
    self.serial.setTimeout( command.timeout )
    log.debug( 'setting timeout: %s' % command.timeout )
    io.info( 'carelink.command: %r\n%s' % ( command,
                                            command.hexdump( ) ) )
    self.write( x )
    log.debug( 'sent command, waiting' )
    time.sleep( command.sleep )
    response = self.read( 64 )
    # log.debug( 'response: %s' % bytearray( response ) )
    reply    = Reply( response )
    log.debug( 'command {0} inspects ACK{1}'.format(
                repr( command ),
                repr( reply.ack ) ) )
    #if reply.ack.isACK( ) or reply.ack.isNAK( ):
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
    return ''.join( [
          '<', '{agent}',
          ':', 'raw={raw}',
          ':', 'flags={flags}'
             , '>' ] ).format(
                raw   = self.raw,
                flags = self.flags,
                agent = self.__class__.__name__
          )

class ACK( object ):
  ACK         = 85  # U
  NAK         = 102 # f
  __ack__     = 'ACK'
  error       = -1
  readable    = -1
  __reason__  = 'UNKNOWN REASON'
  head        = ''
  def __init__( self, head ):
    self.head = head
    try:
      ( self.readable, self.error, self.code ) = head
    except ValueError, e:
      self.__reason__ = '%s:head.length:%s' % ( self.__reason__, len( head ) )
  
  def __repr__( self ):
    return (     self.readable == 1
             and self.error == self.ACK
           ) and self.__ack__  or self.__nak__( )

  def __nak__( self ):
    return '%s:raw:%s' % ( self.reason( ), lib.hexdump( self.head ) )

  def isACK( self ):
    return self.readable == 1 and self.error == self.ACK

  def isNAK( self ):
    return self.readable == 1 and self.error == self.NAK

  def isEmpty( readable ):
    return len( self.head ) == 0

  def reason( self ):
    return self.__reason__
    
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
    self.printable = str( self.msg ).encode( 'string_escape' )


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
    loopingRead( carelink )
  except KeyboardInterrupt:
    print "closing"

  print "Checking status first..."
  pprint( carelink( USBStatus(           ) ).info )
  print "Try resetting radio?..."
  print lib.hexdump( carelink.radio( 64 ) )
  print lib.hexdump( carelink.radio( 64, False ) )
  print lib.hexdump( carelink.radio( 64, False ) )
  pprint( carelink( USBStatus(           ) ).info )
  print "closing for real now"
  carelink.close( )
  sys.exit( 0 )

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
