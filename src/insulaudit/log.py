
import logging
from logging import getLogger
import sys
#logging.basicConfig( stream=sys.stdout )
root = logging.getLogger( 'insulaudit.lib' )
#root.setLevel( logging.DEBUG )

io     = logging.getLogger( 'insulaudit.io' )
logger = logging.getLogger( 'insulaudit.logger' )
config = logging.getLogger( 'insulaudit.config' )


#root.debug( "TEST debug" )
#root.info( "TEST INFO" )
#root.warning( "TEST warning" )
#root.error( "TEST error" )
#root.critical( "TEST crit" )
#root.fatal( "TEST fatal" )

__all__ = [ 'logger', 'io', 'root', 'config' ]

#####
# EOF
