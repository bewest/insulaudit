
from cli.log import LoggingApp
from utils import GlobalOptions
import utils

class Application(LoggingApp):
  """Test Hello World
  """
  name = "insulaudit"
  devices = { }

  def __init__(self):
    kwds = { 'root': True }
    super(Application, self).__init__(**kwds)
  
  def setup(self):
    # just after wrapping argument during __call__
    super(Application, self).setup( )
    utils.setup_global_options(self.argparser)

    self.setup_commands( )

  def pre_run(self):
    # called just before main, updates params, parses args
    super(Application, self).pre_run()
    key           = getattr(self.params, self.dest( ), None)
    device        = self.devices[key]
    self.selected = device
    if callable(device.pre_run):
      device.pre_run(self)

  def dest(self):
    return 'device'

  def help(self):
    return "one line application summary"

  def title(self):
    return self.name

  def get_command_kwds(self):
    fields = [ 'dest', 'title', 'help' ]
    kwds = dict((f, getattr(self, f, None)( )) for f in fields)
    kwds['description'] = self.description
    return kwds

  def setup_commands(self):
    kwds = self.get_command_kwds( )
    self.commands = self.argparser.add_subparsers(**kwds)

  def main(self):
    #pprint(self.params)
    self.selected.main(self)


#####
# EOF
