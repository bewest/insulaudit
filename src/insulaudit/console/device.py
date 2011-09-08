from command import Command
from subcommand import Subcommand
from insulaudit.core import Link
from insulaudit.core import Session
import utils

from insulaudit import scan

from pprint import pprint
class FlowCommand(Subcommand):
  name = None
  def __init__(self, flow, handler, **kwds):
    self.name = kwds.pop('name', getattr(flow, 'name', flow.__name__))
    super(FlowCommand, self).__init__(handler, name=self.name, **kwds)
    self.Flow = flow
    
  def pre_run(self, handler):
    self.handler = handler
    port         = handler.params.port
    if port == 'auto':
      port = scan.best_guess( )
    self.setup_link(port)

  def setup_link(self, port):
    self.log.info('setting up %s' % port)
    self.link = self.handler.selected.link_factory()(port)

  def main(self, app):
    link    = self.link
    session = Session(link, self)
    flow    = self.Flow(session)
    for F in flow( ):
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

  def link_factory(self):
    return Link

  def subcommand_manufacturer(self, flow):
    return FlowCommand(flow, self)

  def setup(self, parser):
    utils.setup_device_options(parser)
    super(LinkCommand, self).setup(parser)

  def pre_run(self, handler):
    super(LinkCommand, self).pre_run(handler)
    self.command = self.subcommands[handler.params.command]
    self.command.pre_run(handler)
    
  def main(self, app):
    self.command.main(app)
    
class ScanningDevice(LinkCommand):
  pass

#####
# EOF
