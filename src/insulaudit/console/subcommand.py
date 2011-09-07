from insulaudit.core import Loggable

class Subcommand(Loggable):
  name = ''
  def __init__(self, session, name=None):
    if name is not None:
      self.name = name
    self.session = session
    self.getLog( )

  def options(self):
    return [ ]

  def setup(self, parser):
    self.parser = parser
    for args, kwds in self.options( ):
      parser.add_argument(*args, **kwds)

  def help(self):
    return self.__doc__

  def main(self, app):
    pprint([self, app])
    print self.name

#####
# EOF
