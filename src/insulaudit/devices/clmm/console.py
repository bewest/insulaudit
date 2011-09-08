
from insulaudit import core

from insulaudit.console import device
import proto

class CLMMApplication(device.LinkCommand):
  """Introducing minimed support. :-)
  """
  name = 'clmm'

  def link_factory(self):
    return proto.Link

  def getFlows(self):
    return [ HelloFlow ]


class HelloFlow(core.Flow):
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
