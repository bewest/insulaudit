
from insulaudit import core

from insulaudit.console import device
import proto

class CLMMApplication(device.LinkCommand):
  """Documentation for CLMMApplication
  """
  name = 'clmm'

  def link_factory(self):
    return proto.Link

  def getFlows(self):
    return [ HelloFlow ]

  def title(self):
    return "clmm - talk with Minimed Paradigm devices"
  def help(self):
    return "testing support for paradigm devices"

class HelloFlow(core.Flow):
  """Hello world for rf comms with MM pumps.
  Can we reliably exchange bytes?
  """
  name = 'hello'
  def flow(self, session):
    link   = session.link
    #link.endCommunicationsIO()
    link.initUSBComms()
    device = proto.initDevice(link)
    self.log.info('got device: %r' % (device))
    link.endCommunicationsIO()

#####
# EOF
