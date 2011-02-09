import logging
from insulaudit.log import io, logger as log
from insulaudit import lib, core

import time

class ACK( object ):
  ACK         = 85  # U
  NAK         = 102 # f
  __ack__     = 'ACK'
  error       = -1
  readable    = -1
  __reason__  = 'UNKNOWN REASON'
  head        = ''
  REASONS     = [ "NO ERROR"
                , "CRC MISMATCH"
                , "COMMAND DATA ERROR"
                , "COMM BUSY AND/OR COMMAND CANNOT BE EXECUTED"
                , "COMMAND NOT SUPPORTED" ]
  def __init__( self, head ):
    self.head = head
    try:
      ( self.readable, self.error, self.code ) = head
    except ValueError, e:
      self.__reason__ = '%s:head.length:%s' % ( self.__reason__, len( head ) )
    print self.code
    self.__reason__ = '%s:%s' % ( self.error, self.REASONS[ self.code ] )
  
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
  
  log     = logging.getLogger( 'reply' )
  ack     = False
  info    = None
  __ACK__ = ACK

  def __init__( self, raw_reply ):
    self.log = logging.getLogger( self.__class__.__name__ )
    self.raw = raw_reply
    self.msg = bytearray( raw_reply )
    try:
      self.ack  = self.__ACK__( self.msg[ 0:3 ] )
      self.body = self.msg[ 3: len(self.msg) - 3 ]
    except IndexError, e:
      raise exceptions.NoReplyException( e )
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

class CarelinkUsb( core.CommBuffer ):
  class ID:
    VENDOR  = 0x0a21
    PRODUCT = 0x8001
  timeout = .150

  #__response__ = core.Reply

  def radio( self, length, crc=True ):
    code = [ 12, 0 ]
    if crc:
      code.extend( [ lib.HighByte( length )
                   , lib.LowByte( length  ) ] )
      code.append( lib.CRC8.compute( code ) )
    self.write( str( bytearray( code ) ) )
    time.sleep( 0.200 )
    return bytearray( self.read( 64 ) )

  def __call__( self, command ):
    self.prevCommand = command
    x = str( command )
    self.serial.setTimeout( command.timeout )
    log.debug( 'setting timeout: %s' % command.timeout )
    io.info( 'carelink.command: %r\n%s' % ( command,
                                            command.hexdump( ) ) )
    self.write( x )
    self.write( x )
    log.debug( 'sent command, waiting' )
    time.sleep( command.sleep )
    reply = command( self )
    return reply
    response = self.read( 64 )
    # log.debug( 'response: %s' % bytearray( response ) )
    reply    = command( response )
    log.debug( 'command {0} inspects ACK{1}'.format(
                repr( command ),
                repr( reply.ack ) ) )
    #if reply.ack.isACK( ) or reply.ack.isNAK( ):
    reply    = command( reply, self )
    return reply
    
if __name__ == '__main__':
  import doctest
  doctest.testmod( )

#####
# EOF
