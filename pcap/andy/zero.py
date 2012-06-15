#!/usr/bin/python

import sys, os
from os.path import getsize
import argparse, itertools

from insulaudit import lib
from insulaudit.log import logger
import logging
logging.basicConfig(stream=sys.stdout)
logger.setLevel(logging.DEBUG)

from pprint import pprint, pformat

CHUNK_SIZE = 32
PROLOG_SIZE = 0

def get_opts():
  parser = argparse.ArgumentParser( )
  parser.add_argument(
    '--chunk', dest='chunk', type=int,
    default=CHUNK_SIZE, help="Default chunksize: %s" % CHUNK_SIZE)
  parser.add_argument(
    '--prolog', dest='prolog', type=int,
    default=PROLOG_SIZE, help="Default prologue size: %s" % PROLOG_SIZE)
  parser.add_argument(
    'input', nargs='+', help="Input files")
  return parser

def get_raw_handle(pathish):
  logger.info('opening %s' % (pathish))
  handle = open(pathish)
  return handle

def hex_dump_data(data):
  print lib.hexdump(bytearray(data))

def read_chunk(handle):
  logger.info('start reading (bytes %s) from offset %s' % (CHUNK_SIZE, handle.tell( )))
  return bytearray(handle.read(CHUNK_SIZE))

def do_chunk(handle):
  chunk = read_chunk(handle)
  hex_dump_data(chunk)

def do_input(pathish):
  handle = get_raw_handle(pathish)
  pos  = handle.tell( )
  size = getsize(pathish)
  logger.info('opening %s (%s bytes)' % (pathish, size))

  logger.info('reading prologue (%s bytes)' % (PROLOG_SIZE))
  prolog = handle.read(PROLOG_SIZE)

  for i in itertools.count( ):
    if pos < size:
      logger.info('chunk: %s' % i)
      do_chunk(handle)
      pos = handle.tell( )
    else:
      break

def main(*args):
  global CHUNK_SIZE, PROLOG_SIZE
  parser = get_opts( )
  args = list(args)
  cmd, args = args[0], args[1:]
  opts = parser.parse_args((args))
  #logger.info('opts: %s' % (pformat(args)))
  CHUNK_SIZE = opts.chunk
  PROLOG_SIZE = opts.prolog
  cmdline = [ cmd,
    '--chunk %s' % (CHUNK_SIZE),
    '--prolog %s' % (PROLOG_SIZE) ] + opts.input
  print ' '.join(cmdline)

  logger.info('opening %s' % (opts.input))

  for item in opts.input:
    do_input(item)

if __name__ == '__main__':
  main(*sys.argv)

#####
# EOF
