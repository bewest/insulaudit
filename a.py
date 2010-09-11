#!/usr/bin/python



import struct
import sys
import serial
import time
import logging
import binascii
from binascii import b2a_hex as dehex
from pprint import pprint, pformat

logging.basicConfig( )
log = logging.getLogger( 'carelink' )
log.setLevel( logging.DEBUG )
log.info( 'hello world' )

example = '\x01U\x00\x00\x02\x00\x00\x00\x05\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

"""
  \x01 U
  \x00 \x00
  \x02 \x00
  \x00 \x00
  \x05 \x04
  \x00 \x00
  \x00 \x00
  \x00 \x00 \x00
  \x00 \x00 \x00
  \x00 \x00 \x00
  \x00 \x00 \x00
  \x00 \x00 \x00
  \x00 \x00 \x00
  \x00 \x00 \x00
  \x00 \x00 \x00
  \x00 \x00 \x00
  \x00 \x00 \x00
  \x00 \x00 \x00
  \x00 \x00 \x00
  \x00 \x00 \x00
  \x00 \x00
  \x00 \x00\x00 \x00 \x00 \x00 \x00 \x00 \x00
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
  timeout     = 0
  sleep       = 0

  min_reply_size  = 64
  def __init__( self, **kwds ):
    self.apply_opts( **kwds )

  def apply_opts( self, **kwds ):
    for i in [ 'code', 'label', 'description', 'timeout', 'sleep' ]:
      setattr( self, i, kwds.get( i, getattr( self, i ) ) )

  def __str__( self ):
    x = str( bytearray( self.code ) )
    log.info( '{label}.encode: {msg}'\
              .format( label=self.label, msg=pformat( x ) ) )
    return x

  def __repr__( self ):
    return '<{agent}:code={code}, label={label}>'\
           .format( code  =repr( self.code ),
                    agent =self.__class__.__name__,
                    label =self.label )

  def __call__( self, device, reply ):
    self.last_reply = reply
    return reply

class USBStatus( Command ):
  """
  """
  code  = [ 3 ]
  ACK   = 85  # U
  NAK   = 102 # f
  label = 'usb.status'
   

class USBProductInfo( Command ):
  """Get product info from the usb device."""
  code   = [ 4 ]
  SW_VER = 16
  label  = 'usb.productInfo'


class USBInterfaceStats( Command ):
  code          = [ 5 ]
  INTERFACE_IDX = 19
  label         = 'usb.interfaceStats'

class USBSignalStrength( Command ):
  code  = [ 6 ]
  label = 'usb.signalStrength'

class USBReadData( Command ):
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
    response = self.readline( )
    # log.debug( 'response: %s' % bytearray( response ) )
    reply    = Reply( response )
    log.debug( 'command {0} inspects {1}'.format(
                repr( command ),
                repr( reply ) ) )
    reply    = command( self, reply )
    return reply
    

class CarelinkException( Exception ): pass

class NoReplyException( CarelinkException ): pass

class Reply( object ):
  log    = logging.getLogger( 'reply' )
  status = 'UNINITIALIZED'
  def __init__( self, raw_reply ):
    self.log = logging.getLogger( self.__class__.__name__ )
    self.raw = raw_reply
    self.msg = bytearray( raw_reply )
    try:
      self.read_status = self.msg[ 0 ]
      self.status      = self.msg[ 2 ]
    except IndexError, e:
      raise NoReplyException( e )
    self.printable = str( self.msg ).encode( 'string_escape' )
    log.debug( 'init reply.raw: %s' % self.printable )


  @staticmethod
  def dehex( S ):
    return [ dehex( l ) for l in S ]

  def __str__( self ):
    return str( self.msg )

  def __repr__( self ):
    return "<{agent}:status={status}:{0}>".format( self.printable,
                                   agent=self.__class__.__name__,
                                   status=self.status )

  @classmethod
  def toDict( klass, response ):
    klass.log.debug( response )
    D       = { 'raw': response }
    S       = klass.dehex( response )
    klass.log.debug( 'dehexed: %s' % S )
    S.reverse( )
    ack     = int( S.pop( ) )
    success = response[ 1 ]
    S.pop( )
    S.reverse( )
    split   = len( S ) - 3
    body    = S[ :split    ]
    tail    = S[  split-1: ]
    D.update( 
      { 'ack'    : ack
      , 'body'   : body
      , 'tail'   : tail
      , 'success': success } )
    klass.log.debug( 'response2dict: %s' % D )
    return D


if __name__ == '__main__':
  print 'hello world'
  


  port = '/dev/ttyUSB0'
  
  carelink = CarelinkUsb( port )
  
  print carelink( USBStatus( ) )
  #print carelink( USBProductInfo( ) )
  #print carelink( USBSignalStrength( ) )
  #print carelink( USBInterfaceStats( ) )
  ##print carelink( USBInterfaceStats( ) )
  #print carelink( USBReadData( timeout = 1 ) )




#####
# EOF
