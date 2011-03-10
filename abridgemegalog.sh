#!/bin/bash
LOG=${1-'megalog'}

# Find the goodies strip out the boring stuff.
grep -A 10 -E "(status reply)|command:" $LOG \
  | grep -v -E 'write|raw|0000|retry|read'

#####
# EOF
