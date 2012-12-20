
import logging
logger = logging.getLogger(__name__)
from core import Link
import glob
import serial
import time

GLOBS = [ '/dev/tty.usb*', '/dev/ttyUSB*' ]

def scan( ):
  """scan all ports, retuns a list of device names."""
  r = [ ]
  for pat in GLOBS:
    r.extend(glob.glob(pat))
  return r

def usable_response(resp):
  logger.debug(resp)
  if resp is not None:
    return True
  return False

def link_usable(candidate):
  usable = False
  try:
    logger.info("attempting to open %s" % candidate)
    #port.port = candidate
    port   = Link(candidate)
    port.open( )
    #port.flush( )
    port.write('')
    port.read(0)
    port.close( )
    del port
    usable = True
  except serial.SerialException: pass
  #port.close( )
  # clmm requires *at least* 5-6 seconds to recover.
  time.sleep(2)

  return usable

def best_guess( ):
  try:
    return filter(link_usable, scan( ))[0]
  except IndexError, e: pass
  return [ ]

if __name__ == '__main__':
  print "Scanning ports:"
  for name in scan( ):
    print name

#####
# EOF
