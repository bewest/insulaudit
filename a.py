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
log = logging.getLogger( )
log.setLevel( logging.DEBUG )
log.info( 'hello world' )

example = '\x01U\x00\x00\x02\x00\x00\x00\x05\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'


class CarelinkStatus( object ):
  code = [ 3 ]
  log  = logging.getLogger( 'carelink.com' )
  def __init__( self ):
    pass

  def encode( self, s ):
    self.log.debug( 'encode: %s' % s )
    r = [ struct.pack( 'H', l ) for l in s ]
    self.log.debug( 'pack( "H", s )= %s' % r )
    return r

  def decode( self, s ):
    return s
    
  def get( self, p ):
    p.write( self.encode( self.code ) )
    time.sleep( 2 )
    return self.decode( p.readline( ) )
    

class Reply( object ):
  log = logging.getLogger( 'RCM' )
  def __init__( self, raw_reply ):
    self.log = logging.getLogger( self.__class__.__name__ )
    log.debug( 'reply.raw: %s' % raw_reply )
    self.raw = raw_reply


  @staticmethod
  def dehex( S ):
    return [ dehex( l ) for l in S ]

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
  S    = serial.Serial( port, timeout=0 )
  
  carelink = CarelinkUsb( port )
  print "ACK, CODE 3"
  S      = carelink.get( S )
  print( Reply.toDict( S ) )

  print
  print "product Info, CODE 4"
  carelink.code = [ 4 ]
  S      = carelink.get( S )
  print( Reply.toDict( S ) )

  print
  print "product rf stats, CODE 5 0"
  carelink.code = [ 5, 0 ]
  S      = carelink.get( S )
  print( Reply.toDict( S ) )

  print
  print "product usb stats, CODE 5 1"
  carelink.code = [ 5, 1 ]
  S      = carelink.get( S )
  print( Reply.toDict( S ) )





#####
# EOF
