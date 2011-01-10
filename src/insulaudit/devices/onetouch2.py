
from insulaudit.log import io, logger as log
from insulaudit import lib, core
from insulaudit.data import glucose
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


def format_glucose( data ):
  """
    >>> date, value = format_glucose( '''P "WED","11/10/10","01:46:00   ''' 
    ...               + '''","  076 ","N","00", 00 099C''' )
    >>> date.isoformat( )
    '2010-11-10T01:46:00'
    >>> value
    76
  """
  try:
    date = lib.parse.date( 'T'.join(
                     data.replace( '"', '' ).split( ',' )[ 1:3 ]) )
    value = int( data.split( '"' )[ 7 ].strip( ) )
  except IndexError, e:
    raise InvalidGlucose( data )
  return date, value

class OneTouch2Exception(core.CarelinkException): pass
class InvalidResponse(OneTouch2Exception): pass
class InvalidGlucose(InvalidResponse): pass

class OneTouchCommand( core.Command ):
  code = HEADER
  response = ''

  def __call__( self, port ):
    self.response = port.readline( ).strip( )
    return self.response

  def decode( self, msg ):
    return str( msg )

  def isEmpty( self, response ):
    return response == ''

class ReadSerial( OneTouchCommand ):
  code = list( bytearray( b'DM@' ) )

class ReadFirmware( OneTouchCommand ):
  code = list( bytearray( b'DM?' ) )

class ReadRFID( OneTouchCommand ):
  code = list( bytearray( b'DMID' ) )

class ReadGlucose( OneTouchCommand ):
  code = list( bytearray( b'DMP' ) )
  def __call__( self, port ):
    head = port.readline( ).strip( )
    body = [ ]
    for line in port.readlines( ):
      try:
        body.append( format_glucose( line ) )
      except InvalidGlucose, e: pass
    io.debug ( 'read glucose:head:%s:body.len:%s' % ( head, len(body) ) )
    self.response = ( head, glucose.l2np( body ) )
    return self.response

  def decode( self, msg ):
    return msg

  def isEmpty( self, *args ):
    return self.response[0] == ''

class OneTouchUltra2( core.CommBuffer ):
  __timeout__ = 20
  __pause__   = 02


  def read_glucose( self ):
    header, body = self.execute( ReadGlucose( ) )
    return header, body

  def wrap( self, data ):
    frame = HEADER + data + [ 0x0D ]
    return bytearray( frame )

  def execute( self, command ):
    """
    """
    msg = self.wrap( command.code )
    # empty meter's buffer before writing anything
    self.readlines( )
    for x in xrange( RETRIES ):
      self.write( str( msg ) )
      time.sleep( self.__pause__ )
      io.info( 'dm read:%s' % x );
      response = command( self )
      if not command.isEmpty( response ):
        break
    io.info( 'get response:%r' % ( repr( response ) ) )
    return command.decode( response )



if __name__ == '__main__':
  import doctest
  doctest.testmod( )

#####
# EOF
