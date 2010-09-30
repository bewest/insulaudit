
from insulaudit.log import io, logger as log
from insulaudit import exceptions
from pprint import pformat
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


#####
# EOF
