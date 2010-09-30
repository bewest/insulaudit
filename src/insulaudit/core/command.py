from insulaudit import core

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
  label       = 'abstract command'
  # Default timeout for a read.
  timeout     = 2
  sleep       = 1
  info        = None

  min_reply_size  = 64
  def __init__( self, **kwds ):
    self.apply_opts( **kwds )

  def apply_opts( self, **kwds ):
    for i in [ 'code', 'label', 'description', 'timeout', 'sleep' ]:
      setattr( self, i, kwds.get( i, getattr( self, i ) ) )

  def __str__( self ):
    x = str( bytearray( self.code ) )
    #s = '{label}: {msg}'.format( label=self.label, msg=self.info )
    return x

  def __repr__( self ):
    return '<{agent}:code={code}, label={label}, info={info}>'\
           .format( code  =repr( self.code ),
                    agent =self.__class__.__name__,
                    label =self.label,
                    info  =self.info )

  def hexdump( self ):
    return lib.hexdump( bytearray( self.code ) )

  def bytez( self ):
    return bytearray( self.code )

  def __call__( self, reply, device=False ):
    self.last_reply = reply
    reply.info = self.info
    return reply

#####
# EOF
