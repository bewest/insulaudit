import loggable

class Session(loggable.Loggable):
  """A session with a serial device is composed of a file like processing
  object (eg a link), and a handler representing the context controlling the
  link.

  """
  link   = None
  handle = None
  def __init__(self, link, handle):
    self.link    = link
    self.handler = handle
    self.getLog( )

#####
# EOF
