
from insulaudit import core

from insulaudit import console
import proto

class CLMMApp(FlowCommand):
  name = 'clmm'


class HelloFlow(core.Flow):
  def flow(self, session):
    link   = session.link
    device = proto.initDevice(link)
    self.log.info('got device: %r' % (device))

#####
# EOF
