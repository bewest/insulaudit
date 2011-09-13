"""A link is a file like object, representing our interesting serial device.
"""

import CommBuffer


class Link(CommBuffer.CommBuffer):
  pass

if __name__ == '__main__':
  import doctest
  doctest.testmod( )

#####
# EOF
