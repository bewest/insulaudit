"""
This module provides some basic helper/formatting utilities.



Module functions:



>>> hexdump( bytearray( [0x00] ) )
'0000   0x00                       .'

>>> 0x00 == HighByte( 0x0F )
True

>>> 0x0F == LowByte( 0x0F )
True


>>> 177 == CRC8.compute( bytearray( [ 0x00, 0xFF, 0x00 ] ) )
True

"""

import doctest

def _fmt_hex( bytez ):
  return ' '.join( [ '%#04x' % x for x in list( bytez ) ] )

def _fmt_txt( bytez ):
  return ''.join( [ chr( x ) if 0x20 <= x < 0x7F else '.' \
                    for x in bytez ] )



def hexdump( src, length=8 ):
  """
  Return a string representing the bytes in src, length bytes per
  line.

  """
  if len( src ) == 0:
    return ''
  result = [ ]
  digits = 4 if isinstance( src, unicode ) else 2
  for i in xrange( 0, len( src ), length ):
    s    = src[i:i+length]
    hexa = ' '.join( [ '%#04x' %  x for x in list( s ) ] )
    text = ''.join( [ chr(x) if 0x20 <= x < 0x7F else '.' \
                    for x in s ] )
    result.append( "%04X   %-*s   %s" % \
                 ( i, length * ( digits + 1 )
                 , hexa, text ) )
  return '\n'.join(result)




def HighByte( arg ):
  return arg >> 8 & 0xFF


def LowByte( arg ):
  return arg & 0xFF




class CRC8:
  lookup = [ 0, 155, 173, 54, 193, 90, 108, 247, 25, 130, 180, 47,
    216, 67, 117, 238, 50, 169, 159, 4, 243, 104, 94, 197, 43, 176,
    134, 29, 234, 113, 71, 220, 100, 255, 201, 82, 165, 62, 8, 147,
    125, 230, 208, 75, 188, 39, 17, 138, 86, 205, 251, 96, 151, 12,
    58, 161, 79, 212, 226, 121, 142, 21, 35, 184, 200, 83, 101, 254,
    9, 146, 164, 63, 209, 74, 124, 231, 16, 139, 189, 38, 250, 97,
    87, 204, 59, 160, 150, 13, 227, 120, 78, 213, 34, 185, 143, 20,
    172, 55, 1, 154, 109, 246, 192, 91, 181, 46, 24, 131, 116, 239,
    217, 66, 158, 5, 51, 168, 95, 196, 242, 105, 135, 28, 42, 177,
    70, 221, 235, 112, 11, 144, 166, 61, 202, 81, 103, 252, 18, 137,
    191, 36, 211, 72, 126, 229, 57, 162, 148, 15, 248, 99, 85, 206,
    32, 187, 141, 22, 225, 122, 76, 215, 111, 244, 194, 89, 174, 53,
    3, 152, 118, 237, 219, 64, 183, 44, 26, 129, 93, 198, 240, 107,
    156, 7, 49, 170, 68, 223, 233, 114, 133, 30, 40, 179, 195, 88,
    110, 245, 2, 153, 175, 52, 218, 65, 119, 236, 27, 128, 182, 45,
    241, 106, 92, 199, 48, 171, 157, 6, 232, 115, 69, 222, 41, 178,
    132, 31, 167, 60, 10, 145, 102, 253, 203, 80, 190, 37, 19, 136,
    127, 228, 210, 73, 149, 14, 56, 163, 84, 207, 249, 98, 140, 23,
    33, 186, 77, 214, 224, 123 ]

  @classmethod
  def compute( klass, block ):
    result = 0
    for i in xrange( len( block ) ):
      result = klass.lookup[ ( result ^ block[ i ] & 0xFF ) ]
    return result


if __name__ == '__main__':
  doctest.testmod( )

#####
# EOF
