
devices = { }

def get_consoles( ):
  from clmm.console import CLMMApplication
  from onetouch.console import OnetouchApp
  return [ CLMMApplication, OnetouchApp ]

#####
# EOF
