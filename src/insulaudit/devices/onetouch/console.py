
from insulaudit import core
from insulaudit.data import glucose

from insulaudit.console import device
import proto

class OnetouchApp(device.LinkCommand):
  """Onetouch compatible lifescan devices.
  """
  name = 'onetouch'

  def link_factory(self):
    return proto.Link
    #return proto.Linonetouch2.OneTouchUltra2( PORT, 5 )

  def getFlows(self):
    return [ HelloFlow, sugars ]

  def title(self):
    return "onetouch - talk with Lifescan OneTouch compatible devices."
  def help(self):
    return "talk with Lifescan OneTouch compatible devices"

  def subcommand_manufacturer(self, flow):
    return OTCommand(flow, self)

class OTCommand(device.FlowCommand):
  def setup_link(self, port):
    self.log.info('setting up %s' % port)
    return self.handler.selected.link_factory()(port, 5)

class HelloFlow(core.Flow):
  """Hello world for Lifescan onetouch compatible devices.
  Can we reliably exchange bytes?
  """
  name = 'hello'
  def flow(self, session):
    link   = session.link
    serial = link.execute( proto.ReadSerial( ) )
    print "serial number: %s" % serial 
    session.log.info("serial number: %s" % serial)
    firmware = link.execute( proto.ReadFirmware( ) )
    print "firmware: %s" % firmware 
    session.log.info("firmware: %s" % firmware)
    session.log.info('done')

class sugars(core.Flow):
  """Dump the sugars to stdout
  Can we reliably exchange bytes?
  """
  #name = 'sugars'
  def get_out_file(self):
    import sys
    return sys.stdout

  def flow(self, session):
    link = session.link
    serial = link.execute( proto.ReadSerial( ) )
    data = link.read_glucose( )
    print data
    print "len glucose: %s" % len( data )
    head, body = data 
    print glucose.format_records( body )

#####
# EOF
