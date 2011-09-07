
from cli.log import LoggingApp
from utils import GlobalOptions
import utils

class Application(LoggingApp):
  """Test Hello World
  """
  name = "insulaudit"
  devices = { }
  
  def setup(self):
    # just after wrapping argument during __call__
    #super(type(self), self).setup( )
    #GlobalOptions.setup(self)
    super(Application, self).setup( )
    #GlobalOptions.setup(self)
    #self.add_param("bar", help="fake option", action='store_true')
    utils.setup_global_options(self.argparser)
    self.commands = self.argparser.add_subparsers(dest='device', help='fake help on this command')

    self.setup_commands( )
  def pre_run(self):
    # called just before main, updates params, parses args
    super(Application, self).pre_run()
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

  def main(self):
    self.log.warn("hello world warn")
    self.log.debug("hello world debug")
    self.log.info("hello world info")
    self.log.error("hello world error")
    self.log.critical("hello world critical")
    self.log.fatal("hello world fatal")
    pprint(self.params)
    self.selected.main(self)

#####
# EOF
