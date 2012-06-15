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

CHUNK_SIZE = 64

def get_opts():
  parser = argparse.ArgumentParser( )
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
  logger.info('start reading: %s' % handle.tell( ))
  return bytearray(handle.read(64))

def do_chunk(handle):
  chunk = read_chunk(handle)
  hex_dump_data(chunk)

def do_input(pathish):
  handle = get_raw_handle(pathish)
  pos  = handle.tell( )
  size = getsize(pathish)
  logger.info('opening %s (%s bytes)' % (pathish, size))

  for i in itertools.count( ):
    if pos < size:
      logger.info('chunk: %s' % i)
      do_chunk(handle)
      pos = handle.tell( )
    else:
      break




def main(*args):
  parser = get_opts( )
  opts = parser.parse_args( )
  logger.info('opening %s' % (opts.input))

  for item in opts.input:
    do_input(item)


  


if __name__ == '__main__':
  main(sys.argv )

