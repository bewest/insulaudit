
from insulaudit.log import io, logger as log
from insulaudit import lib, core
import time

HEADER = [ 0x11, 0x0D ]
STX = 0x02
ETX = 0x03
TIMEOUT = 0.5

RETRIES = 3


def ls_long( B ):
  B.reverse( )
  return lib.BangLong( B )
  
def ls_int( B ):
  B.reverse( )
  return lib.BangInt( B )


class OneTouch2Exception(core.CarelinkException): pass

class OneTouchCommand( core.Command ):
  code = HEADER

  def decode( self, msg ):
    return str( msg )

class ReadSerial( OneTouchCommand ):
  code = list( bytearray( b'DM@' ) )

class ReadFirmware( OneTouchCommand ):
  code = list( bytearray( b'DM?' ) )

class ReadRFID( OneTouchCommand ):
  code = list( bytearray( b'DMID' ) )

class ReadGlucose( OneTouchCommand ):
  code = list( bytearray( b'DMP' ) )

class OneTouchUltra2( core.CommBuffer ):
  __timeout__ = 20
  __pause__   = 02


  def read_glucose( self ):
    header = self.execute( ReadGlucose( ) )
    length = int( header.split( )[ 1 ][ :3 ] )
    rows = self.readlines( )
    return rows

  def wrap( self, data ):
    frame = HEADER + data + [ 0x0D ]
    return bytearray( frame )

  def execute( self, command ):
    """
    """
    msg = self.wrap( command.code )
    #time.sleep( self.__pause__ * 5 )
    # meter sends DATA
    self.readlines( )
    for x in xrange( RETRIES ):
      self.write( str( msg ) )
      time.sleep( self.__pause__ )
      io.info( 'dm read:%s' % x );
      response = bytearray( self.readlines( ) )
      if response != '':
        break
    io.info( 'get response:%s' % response );
    # PC sends ACK
    return command.decode( response )

  def __call__( self, command ):
    self.prevCommand = command


if __name__ == '__main__':
  import doctest
  doctest.testmost( )

#####
# EOF
