from command import Command
from subcommand import Subcommand
from insulaudit.core import Link
from insulaudit.core import Session
import utils

class FlowCommand(Subcommand):
  def __init__(self, flow, handler, **kwds):
    name = kwds.pop('name', flow.__class__.__name__)
    super(FlowCommand, self).__init__(handler, name=name, **kwds)
    self.Flow = flow
    
  def main(self, app):
    link    = Link(app.options.port)
    session = Session(link, self)
    flow    = self.Flow(session)
    for F in self.flow( ):
      F(session)

class LinkCommand(Command):
  """Processes flows."""
  def __init__(self, **kwds):
    super(LinkCommand, self).__init__( )
    for Flow in self.getFlows( ):
      self.addFlow(Flow)

  def getFlows(self):
    """Give subclasses an opportunity to advertise their own flows."""
    return [ ]

  def subcommand_manufacturer(self, flow):
    return FlowCommand(flow, self)

  def setup(self, parser):
    utils.setup_device_options(parser)

  def pre_run(self, handler):
    super(type(self), self).pre_run( )
    self.command = self.flows[app.params.command]
    
  def main(self, app):
    self.command.main(self.session)
    
class ScanningDevice(LinkCommand):
  pass

#####
# EOF
