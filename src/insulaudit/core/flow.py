
import loggable

class Flow(loggable.Loggable):
  session = None
  def __init__(self, session):
    self.session = session
    self.getLog( )

  def __call__(self):
    """Execute callable produces an iterable."""
    yield self.flow
    raise StopIteration

  def flow(self, req):
    """
    Execute this flow.
    req

    ``req.io`` should be 


    """
    # a file like object, probably a serial device
    link = req.link
    self.log.info("hello world: %r:%r" % (self, self.__dict__))

if __name__ == '__main__':
  import doctest
  doctest.testmod( )

#####
# EOF
