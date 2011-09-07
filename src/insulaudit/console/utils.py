
def setup_device_options(parser):
  parser.add_argument("--port",
    help="/dev/ttyUSB0, path to serial port",
    type=str, default='auto', required=True)

def setup_global_options(parser):
  # Set up global options
  #parser.add_param("--device", help="device", action='store_true')
  #print "setting up global options"
  parser.add_argument("--bar", help="fake fake serial port", type=str, default='auto')

class GlobalOptions(object):
  def setup_global_options(self, parser):
    # Set up global options
    #self.add_param("--device", help="device", action='store_true')
    setup_global_options(parser)
    #print "setting up global options"

#####
# EOF
