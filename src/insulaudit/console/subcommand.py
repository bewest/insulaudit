from insulaudit.core import Loggable

class Subcommand(Loggable):
  name = None
  def __init__(self, handler, name=None):
    if name is not None:
      self.name = name
    self.handler = handler
    self.getLog( )

  def options(self):
    # should return a list of tuples to be passed as *args, **kwds to
    # argparser's parse.add_argument
    return [ ]

  def setup(self, parser):
    self.parser = parser
    for args, kwds in self.options( ):
      parser.add_argument(*args, **kwds)

  def help(self):
    return self.__doc__

  def main(self, app):
    #pprint([self, app])
    print self.name

#####
# EOF
