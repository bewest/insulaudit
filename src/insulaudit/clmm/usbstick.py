from insulaudit.log import io, logger as log
from insulaudit import lib, core

class CarelinkUsb( core.CommBuffer ):
  class ID:
    VENDOR  = 0x0a21
    PRODUCT = 0x8001
  timeout = .150

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
    
if __name__ == '__main__':
  import doctest
  doctest.testmost( )

#####
# EOF
