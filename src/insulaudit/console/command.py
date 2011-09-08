from insulaudit.core import Loggable

class Command(Loggable):
  """A base command to help with CLI.
  """
  subcommands = { }
  name = None
  dest = 'command'
  def __init__(self, name=None, subcommands=None):
    self.subcommands = { }
    self.getLog( )
    if self.name is None:
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

  def setup_subparser(self):
    self.subparser = parser.add_subparsers(dest=self.dest, help=self.help( ))

  def setup(self, parser):
    n = self.name
    self.parser   = parser
    self.commands = parser.add_subparsers(dest=self.dest, help=self.help( ))
    for flow in self.subcommands.values( ):
      p = self.commands.add_parser(flow.name, help=flow.help())
      flow.setup(p)

  def pre_run(self, handler):
    self.handler = handler
 
  def main(self, app):
    subcommand = self.subcommands[app.params.command]
    subcommand.main(app)

  def help(self):
    return self.__doc__

#####
# EOF
