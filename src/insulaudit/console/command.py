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
      self.add_subcommands(subcommands)

  def add_subcommands(self, subcommands):
    for flow in subcommands:
      self.addFlow(flow)

  def addFlow(self, Flow):
    flow = self.subcommand_manufacturer(Flow)
    self.subcommands[flow.name] = flow

  def subcommand_manufacturer(self, flow):
    return flow(self)

  def get_subparser_kwds(self):
    fields = [ 'title', 'help', 'description' ]
    kwds = dict((f, getattr(self, f, None)( )) for f in fields)
    kwds['dest'] = self.dest
    return kwds

  def setup_subparser(self):
    kwds = self.get_subparser_kwds( )
    self.subparser = self.parser.add_subparsers(**kwds)

  def setup(self, parser):
    n = self.name
    self.parser   = parser
    self.setup_subparser()
    for flow in self.subcommands.values( ):
      p = self.subparser.add_parser(flow.name, help=flow.help())
      flow.setup(p)

  def pre_run(self, handler):
    self.handler = handler
 
  def main(self, app):
    subcommand = self.subcommands[app.params.command]
    subcommand.main(app)

  def help(self):
    """More like a one line summary."""
    return "%s's one line summary" % self.name

  def title(self):
    return "%s's command title" % self.name

  def description(self):
    return "%s's command description" % self.__doc__

#####
# EOF
