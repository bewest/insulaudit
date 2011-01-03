
from insulaudit.log import io, logger as log
from insulaudit import lib, core
import time

STX = 0x02
ETX = 0x03
TIMEOUT = 0.5

RETRIES = 3

class CRCMismatch(Exception): pass

class LSUltraMini( core.CommBuffer ):
  __timeout__ = 0.5
  __control__ = None

  def disconnect( self ):
    msg = [ STX, 0x06, 0x08, ETX ]
    crc = lib.CRC16CCITT.compute( msg )
    msg.extend( [ lib.LowByte( crc ), lib.HighByte( crc ) ] )
    io.info( 'disconnect' )
    self.write( str( bytearray( msg ) ) )
    for i in xrange( RETRIES ):
      r = bytearray( self.read( 40 ) )
      if r == '':
        io.debug( "NOTHING TRY: %s" % i )
      else:
        break
    io.info( lib.hexdump( r ) )


    
  def format_packet( self, bytez ):
    pass

  def __call__( self, command ):
    self.prevCommand = command


if __name__ == '__main__':
  import doctest
  doctest.testmost( )

#####
# EOF
