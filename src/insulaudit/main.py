#!/usr/bin/python

from cli.log import LoggingApp
from insulaudit import core
from pprint import pprint

"""
Very rough.
"""

class DeviceFlow(object):
  name = ''
  def __init__(self, session):
    self.session = session

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

class QuxApp(DeviceFlow):
  """Qux Does several special things"""
  name = "qux"
class FuxApp(DeviceFlow):
  """Fux is accidently different."""
  name = "fux"
class BuxApp(DeviceFlow):
  """Bux seems special, but it's a trick."""
  name = "bux"

class Flow(object):
  pass

class Session(object):
  pass

class BaseDevice(object):
  "Fake help"
  flows = { }
  def __init__(self, name, flows=None):
    self.name  = name
    if flows is not None:
      for Flow in flows:
        self.addFlow(Flow(self))
      #self.flows.update(dict([(F.name, F(self)) for F in flows ]))
      #self.flows = flows

  def addFlow(self, flow):
    self.flows[flow.name] = flow

  def setup(self, parser):
    n = self.name
    self.parser   = parser
    self.commands = parser.add_subparsers(dest='command', help=self.help( ))
    for flow in self.flows.values( ):
      #flow = Flow( )
      p = self.commands.add_parser(flow.name, help=flow.help())
      flow.setup(p)
 
  def help(self):
    return self.__doc__

def get_devices():
  devices = [ ]
  a = BaseDevice('AAA', [ FuxApp, QuxApp, BuxApp ] )
  b = BaseDevice('BBB', [ FuxApp, QuxApp, BuxApp ] )
  return [ a, b ]

class GlobalOptions(object):
  def setup_global_options(self):
    # Set up global options
    self.add_param("--device", help="device", action='store_true')
    #print "setting up global options"

class Application(LoggingApp):
  """Test Hello World
  """
  name = "insulaudit"
  devices = { }
  
  def __init__(self):
    super(type(self), self).__init__( )
  def setup(self):
    # just after wrapping argument during __call__
    super(type(self), self).setup( )
    pprint(self.log)
    #GlobalOptions.setup(self)
    #super(LoggingApp, self).setup( )
    #GlobalOptions.setup(self)
    #self.add_param("bar", help="fake option", action='store_true')
    #self.setup_global_options( )
    self.commands = self.argparser.add_subparsers(dest='device', help='fake help on this command')

    for dev in get_devices():
      self.add_device( dev )
    #self.foo = self.commands.add_parser('device', help="foo help")
    #self.foo.add_argument('comm', help='free form')
  def pre_run(self):
    # called just before main, updates params, parses args
    super(type(self), self).pre_run()
    #GlobalOptions.pre_run(self)
    pprint(self.__dict__)
    #LoggingApp.pre_run(self)
    #super(LoggingApp, self).pre_run( )
    device  = self.devices[self.params.device]
    command = device.flows[self.params.command]
    self.selected = command.main

    # set up serial port

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
    self.selected(self)
    

if __name__ == '__main__':
  app = Application()
  app.run( )

#####
# EOF
