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
  except (IndexError, ValueError), e:
    log.info( data )
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

class UltraSmartWakeUp1( OneTouchCommand ):
  code = bytearray( [ 0xB0, 0x04, 0x00, 0x00, 0x00, 0x00, 0x07 ] )

class UltraSmartWakeUp2( OneTouchCommand ):
  code = bytearray( [ 0x80, 0x25, 0x00, 0x00, 0x00, 0x00, 0x07,
                            0x80, 0x25, 0x00, 0x00, 0x00, 0x00, 0x08 ] )
  def __call__(self, port ):
    return True

class UltraSmartWakeUpStage1( OneTouchCommand ):
  #code = bytearray( [ 0x00, 0x96, 0x00, 0x00, 0x00, 0x00, 0x08 ] )
  code  = bytearray( [ 0x11, 0x0D, ] )
  def __call__(self, port ):
    stuff = port.write("")
    #time.sleep(5)
    stuff = port.readlines( )
    io.info( "RECIEVED HANDSHAKE REPLY: %s bytes" % len(stuff) )
    io.info(lib.hexdump(bytearray( stuff )))
    if len(stuff) > 0:
      return True
    return False


class UltraSmartWakeUpStage2( OneTouchCommand ):
  code = bytearray( [ 0x80, 0x25, 0x00, 0x00, 0x00, 0x00, 0x08,
                      0x80, 0x25, 0x00, 0x00, 0x00, 0x00, 0x08,
                      0x11, 0x11, 0x0D, 0x0D, 0x44, 0x44, 0x4D,
                      0x4D, 0x53, 0x53, 0x0D, 0x0D, 0x0D, 0x0D,
                      0x11, 0x11, 0x0D, 0x0D, 0x44, 0x44, 0x4D,
                      0x4D, 0x53, 0x53, 0x0D, 0x0D, 0x0D, 0x0D,
                      0x00, 0x96, 0x00, 0x00, 0x00, 0x00, 0x08,
                      0x00, 0x96, 0x00, 0x00, 0x00, 0x00, 0x08,
                      0x11, 0x11, 0x0D, 0x0D, 0x44, 0x44, 0x4D,
                      0x4D, 0x53, 0x53, 0x0D, 0x0D, 0x0D, 0x0D,
                      0x11, 0x11, 0x0D, 0x0D, 0x44, 0x44, 0x4D,
                      0x4D, 0x40, 0x40, 0x0D, 0x0D ] )

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

  def stage1_wakeup(self):
    io.info("wakeup: stage 1")
    command = UltraSmartWakeUpStage1( )
    msg = bytearray( command.code )
    for x in xrange( RETRIES ):
      self.write( str( msg ) )
      #self.write( str( msg ) )
      time.sleep( self.__pause__ )
      response = command( self )
      if response:
        break
    io.info( 'get response:%s' % ( response ) )
    if not response:
      raise OneTouch2Exception("NOT A GOOD START")

  def stage2_wakeup(self):
    stage2a = [ 0x80, 0x25, 0x00, 0x00, 0x00, 0x00, 0x07 ]
    stage2b = [ 0x80, 0x25, 0x00, 0x00, 0x00, 0x00, 0x08 ]
    stage2c = [ 0x11, 0x0D, 0x44, 0x4D, 0x53, 0x0D, 0x0D ]
    stage2d = [ 0x11, 0x0D, 0x44, 0x4D, 0x53, 0x0D, 0x0D ]
    stage2e = [ 0x00, 0x96, 0x00, 0x00, 0x00, 0x00, 0x08 ]
    stage2f = [ 0x11, 0x0D, 0x44, 0x4D, 0x53, 0x0D ]
    stages = [ stage2a, stage2b, stage2c, stage2d, stage2e, stage2f, ]
    awake = False
    for stage in stages:
      msg = bytearray(stage)
      self.write( str( msg ) )
      response = self.readlines( )
      if len(response) > 0:
        io.info("got a response!!!")
        io.info(lib.hexdump(bytearray(response)))
        awake = True
    return awake
  
  def wakeup_smart( self ):
    io.info("begin wakeup")
    self.stage1_wakeup( )
    self.stage2_wakeup( )
    #stage2 = UltraSmartWakeUpStage2( )
    #self.write( str( stage2.code ) )
    #response_2 = stage2( self )
    #self.write( str( wake1.code ) )
    time.sleep( self.__pause__ )
    
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
      self.write( str( msg ) )
      time.sleep( self.__pause__ )
      io.info( 'dm read:%s' % x );
      response = command( self )
      if not command.isEmpty( response ):
        break
    io.info( 'get response:%r' % ( repr( response ) ) )
    return command.decode( response )

class Link(OneTouchUltra2):
  pass


if __name__ == '__main__':
  import doctest
  doctest.testmod( )

#####
# EOF
