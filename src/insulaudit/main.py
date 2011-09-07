#!/usr/bin/python

from cli.log import LoggingApp
from insulaudit import core
from pprint import pprint

"""
Very rough.
"""

class Flow(core.Loggable):
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

    ``req.link`` should be 


    """
    # a file like object, probably a serial device
    link = req.link
    self.log.info("hello world: %r:%r" % (self, self.__dict__))


class Link(core.CommBuffer):
  pass


class Subcommand(core.Loggable):
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

class QuxApp(Subcommand):
  """Qux Does several special things"""
  name = "qux"
class FuxApp(Subcommand):
  """Fux is accidently different."""
  name = "fux"
class BuxApp(Subcommand):
  """Bux seems special, but it's a trick."""
  name = "bux"

class Session(core.Loggable):
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


class Command(object):
  "Fake help"
  subcommands = { }
  def __init__(self, name=None, subcommands=None):
    if name is None:
      name = self.__class__.__name__
    self.name  = name
    if subcommands is not None:
      for flow in subcommands:
        self.addFlow(flow)

  def addFlow(self, Flow):
    flow = self.subcommand_manufacturer(Flow)
    self.subcommands[flow.name] = flow

  def subcommand_manufacturer(self, flow):
    return flow(self)

  def setup(self, parser):
    n = self.name
    self.parser   = parser
    self.commands = parser.add_subparsers(dest='command', help=self.help( ))
    for flow in self.subcommands.values( ):
      #flow = Flow( )
      p = self.commands.add_parser(flow.name, help=flow.help())
      flow.setup(p)

  def pre_run(self, handler):
    # Create a session here
    self.handler = handler
    pass
 
  def main(self, app):
    command = self.subcommands[app.params.command]
    command.main(app)

  def help(self):
    return self.__doc__

class LinkFlow(Subcommand):
  def __init__(self, flow, **kwds):
    super(type(self), self).__init__(**kwds)
    self.Flow = flow
    
  def main(self, app):
    link    = Link(app.options.port)
    session = Session(link, self)
    for F in self.flow( ):
      F(session)


class DeviceCommand(Command):
  """Processes flows."""
  def __init__(self, **kwds):
    super(type(self), self).__init__( )
    for Flow in self.getFlows( ):
      self.addFlow(Flow)

  def getFlows(self):
    """Give subclasses an opportunity to advertise their own flows."""
    return [ ]

  def subcommand_manufacturer(self, flow):
    return LinkFlow(flow)

  def addFlow(self, Flow):
    flow = self.subcommand_manufacturer(Flow)
    self.flows[flow.name] = flow
  def setup(self, parser):
    setup_device_options(parser)

  def pre_run(self, handler):
    super(type(self), self).pre_run( )
    self.command = self.flows[app.params.command]
    
  def main(self, app):
    self.command.main(self.session)
    


class ScanningDevice(DeviceCommand):
  pass

def setup_device_options(parser):
  parser.add_argument("--port",
    help="/dev/ttyUSB0, path to serial port",
    type=str, default='auto', required=True)

def get_devices():
  devices = [ ]
  a = Command('AAA', [ FuxApp, QuxApp, BuxApp ] )
  b = Command('BBB', [ FuxApp, QuxApp, BuxApp ] )
  return [ a, b ]

def setup_global_options(parser):
  # Set up global options
  #parser.add_param("--device", help="device", action='store_true')
  #print "setting up global options"
  parser.add_argument("--bar", help="fake fake serial port", type=str, default='auto')

class GlobalOptions(object):
  def setup_global_options(self, parser):
    # Set up global options
    #self.add_param("--device", help="device", action='store_true')
    setup_global_options(parser)
    #print "setting up global options"

class Application(LoggingApp, GlobalOptions):
  """Test Hello World
  """
  name = "insulaudit"
  devices = { }
  
  def __init__(self):
    super(type(self), self).__init__( )
  def setup(self):
    # just after wrapping argument during __call__
    super(type(self), self).setup( )
    #GlobalOptions.setup(self)
    #super(LoggingApp, self).setup( )
    #GlobalOptions.setup(self)
    #self.add_param("bar", help="fake option", action='store_true')
    setup_global_options(self.argparser)
    self.commands = self.argparser.add_subparsers(dest='device', help='fake help on this command')

    for dev in get_devices():
      self.add_device( dev )
    #self.foo = self.commands.add_parser('device', help="foo help")
    #self.foo.add_argument('comm', help='free form')
  def pre_run(self):
    # called just before main, updates params, parses args
    super(type(self), self).pre_run()
    #GlobalOptions.pre_run(self)
    #pprint(self.__dict__)
    #LoggingApp.pre_run(self)
    #super(LoggingApp, self).pre_run( )
    device  = self.devices[self.params.device]
    if callable(device.pre_run):
      device.pre_run(self)
    self.selected = device
    #self.selected = command = device.flows[self.params.command]
    #self.selected = command.main


  def add_device(self, device):
    self.devices[device.name] = device
    parser = self.commands.add_parser(device.name, help=device.help())
    device.setup(parser)

  def main(self):
    self.log.warn("hello world warn")
    self.log.debug("hello world debug")
    self.log.info("hello world info")
    self.log.error("hello world error")
    self.log.critical("hello world critical")
    self.log.fatal("hello world fatal")
    pprint(self.params)
    self.selected.main(self)
    

if __name__ == '__main__':
  app = Application()
  app.run( )

#####
# EOF
