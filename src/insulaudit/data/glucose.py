
import dateutil.parser
import string
from insulaudit.log import logger as log
from datetime import datetime
import numpy as np
import time

"""Convert everything in and out of numpy."""
DTYPES = [( 'time', np.dtype( datetime ) ), ( 'value', np.int) ]


def _date2epoch( date ):
  return time.mktime( date.timetuple( ) )

def text2date( a ):
  return dateutil.parser.parse( a )

def get_days( days ):
  # XXX: missing fill missing days
  days = np.unique( ( d.date( ) for d in days ) )
  return days

date2epoch = np.vectorize( _date2epoch,  otypes=[ np.float ] )

def parse_text( text ):
  """
  A glucose record is a tuple of the time and glucose.
    ( datetime.datetime, int )

  >>> len( parse_text(  '''2011-01-01 01:02  076''' )[ 0 ] )
  2

  # spaces
  >>> date, value = parse_text(  '''2011-01-01 01:02  076''' )[ 0 ]
  ... #
  >>> date.isoformat( )
  '2011-01-01T01:02:00'
  >>> value
  76

  # tabs
  >>> date, value = parse_text(  '''2011-01-01T01:02	076 ''' )[ 0 ]
  >>> (date.isoformat( ), value)
  ('2011-01-01T01:02:00', 76)

  # T
  >>> date, value = parse_text(  '''2011-01-01T01:02	076''' )[ 0 ]
  >>> date.isoformat( ), value
  ('2011-01-01T01:02:00', 76)

  # PM/AM
  >>> date, value = parse_text(  '''2011-01-01 01:02AM 076''' )[ 0 ]
  >>> date.isoformat( ), value
  ('2011-01-01T01:02:00', 76)
  >>> date, value = parse_text(  '''2011-01-01 01:02PM 076''' )[ 0 ]
  >>> date.isoformat( ), value
  ('2011-01-01T13:02:00', 76)
  >>> date, value = parse_text(  '''2011-01-01	01:02PM 076''' )[ 0 ]
  >>> date.isoformat( ), value
  ('2011-01-01T13:02:00', 76)


  """
  # TODO: sensitivity to timezones!
  results = [ ]
  for datum in text.splitlines( ):
    frags = datum.strip( ).split( )
    if frags == [ ]: continue
    log.info( frags )
    #frags = map( string.strip, datum.strip( ).split( ) )
    value = int( frags[ -1 ] )
    date  = None
    try:
      date = text2date( ' '.join( frags[ 0:-1 ] ) )
      results.append( ( date, value ) )
    except IndexError, e:
      log.error( 'error %s' % ( e ) )

  return np.array( results, dtype=DTYPES ).view( np.recarray, )

def l2np( L ):
  return np.array( L, dtype=DTYPES ).view( np.recarray, )

def format_records( records ):
  """
    Format a list of records into text.
  """
  text = [ ]
  for ( date, value ) in records:
    text.append( '\t'.join( [ date.isoformat( ), str( value ) ] ) )
  return '\n'.join( text )

class DataProvenance( object ):
  pass

class MissingProvenance( DataProvenance ):
  pass

class GlucoseRecords( object ):
  def __init__( self, records, provenance=None ):
    self.records    = records
    self.provenance = provenance


"""
  >>> (np_file( 'test.txt' ) == load_file( 'test.txt' )).all( )
  True
"""



def np_file( filename ):
  """
    >>> len( np_file( 'test.txt' ) )
    10

    chokes on wonky separators
  """
  converters = { 'time': text2date }
  return np.genfromtxt( filename, dtype=DTYPES,
                        converters=converters ).view(np.recarray)


def load_file( filename ):
  records = [ ]
  F = open( filename, 'r' )
  records = parse_text( F.read( ) )
  F.close( )
  return records


if __name__ == '__main__':
  import doctest
  doctest.testmod( )

#####
# EOF
