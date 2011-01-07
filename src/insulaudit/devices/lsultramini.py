
from insulaudit.log import io, logger as log
from insulaudit import lib, core
import time

STX = 0x02
ETX = 0x03
TIMEOUT = 0.5

RETRIES = 3

"""
Bit 7
  Unused
Bit 6
  Unused
Bit 5
  Unused
Bit 4
  More
Bit 3
  Disconnect
Bit 2
  Acknowledge
Bit 1
  E
Bit 0
  S


"""

class Link:
  SEND = 0x01
  RECE = 0x01 << 1
  ACK  = 0x01 << 2
  DISC = 0x01 << 3



class Response( object ):
  __raw__ = None
  def __init__( self, raw=None ):
    self.__raw__ = None
    if raw is not None:
      self.__raw__ = raw

  def validate( self ):
    self.bytez = bytearray( self.__raw__ )
    if self.bytez[ 0 ] != STX:
      raise InvalidResponse(raw)
    self.length = self.raw[ 1 ]
    
  def incr( self, raw ):
    if self.__raw__ is None:
      self.__raw__ = ''
    self.__raw__ = self.__raw__ + raw
     
    msg = self.__raw__[0]
    if msg != STX:
      raise InvalidResponse(msg)
    


class LSException(core.CarelinkException): pass
class InvalidResponse(LSException): pass
class MissingAck(LSException): pass

class CRCMismatch(LSException): pass

class DiscoverFirmware( core.Command ):
  code = [ 5, 13, 2 ]
  def decode( self, msg ):
    return str( msg[ 3: len(msg) - 3 ] )



class LSUltraMini( core.CommBuffer ):
  __timeout__ = 0.5
  __pause__   = 02

  def disconnect( self ):
    msg = list( self.wrap( 0x08, [ ] ) )
    io.info( 'disconnect' )
    self.__retry_write_with_ack__( msg, RETRIES )

  def __retry_write_with_ack__( self, msg, retries ):
    try:
      for i in xrange( RETRIES - 1 ):
        try:
          self.write( str( bytearray( msg ) ) )
          io.info( '__retry_write_with_ack__::%i' % i )
          self.__ack__ = self.__requireAck__( )
          return self.__ack__
        except MissingAck, e:
          io.info( 'retry:%s:missing ack:%r' % ( i, e ) )
      self.write( str( bytearray( msg ) ) )
      self.__ack__ = self.__requireAck__( )
    # catch
    except MissingAck, e:
      #except Exception, e:
      io.fatal( 'noticed and uncaught: %r' % e )
      raise
    return self.__ack__

    

  def __requireAck__( self ):
    """Try to read an ack, raising MissingAck if we don't read it. Returns
    bytearray ack."""
    ack = None
    for i in xrange( RETRIES ):
      ack = bytearray( self.read( 6 ) )
      if ack == '':
        io.debug( "empty ack:%s:%s:sleeping:%s" % ( i, ack, self.__pause__ ) )
        time.sleep( self.__pause__ )
      else:
        break
    io.info( 'ACK: %s' % lib.hexdump( ack ) )
    if ack == '':
      raise MissingAck(i)
    return ack
    
  def __acknowledge__( self ):
    msg = [ STX, 6, 0x04 | 0x08, ETX ]
    crc = lib.CRC16CCITT.compute( msg )
    msg.extend( [ lib.LowByte( crc ), lib.HighByte( crc ) ] )
    io.info( 'sending ACK' )
    self.write( str( bytearray( msg ) ) )

  def __send__require_ack__( self, command ):
    """sending a command requires an ack from the device every time."""
    io.debug( 'command:\n%s' % command )
    # PC sends command
    # meter sends ACK
    msg = str( self.wrap( 0, command.code ) )
    return self.__retry_write_with_ack__( msg, RETRIES )
    # TODO: process ack here?
    #self.write( msg )
    # self.__requireAck__( )
    
  def wrap( self, link, data ):
    frame = [ STX, len( data ) + 6, link ] + data + [ ETX ]
    crc   = lib.CRC16CCITT.compute( frame )
    frame.extend( [ lib.LowByte( crc ), lib.HighByte( crc ) ] )
    return bytearray( frame )

  def execute( self, command ):
    """
    XXX: Handles retries, link control, and message validation?
    """
    link = 0
    # TODO: validate against CRC/ACK
    r = self.__send__require_ack__( command )
    # meter sends DATA
    response = bytearray( self.read( 40 ) )
    io.info( 'get response:%s' % response );
    # PC sends ACK
    self.__acknowledge__( )
    return command.decode( response )

  def __call__( self, command ):
    self.prevCommand = command


if __name__ == '__main__':
  import doctest
  doctest.testmost( )

#####
# EOF
