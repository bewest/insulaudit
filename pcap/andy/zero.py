#!/usr/bin/python

import sys
import argparse

from insulaudit import lib
from insulaudit.log import logger
import logging
logging.basicConfig(stream=sys.stdout)
logger.setLevel(logging.DEBUG)

from pprint import pprint, pformat

def get_opts():
  parser = argparse.ArgumentParser( )
  parser.add_argument(
    'input', nargs='+', help="Input files")
  return parser

def main(*args):
  parser = get_opts( )
  opts = parser.parse_args(*args)
  logger.info('hello world %r %s' % (args, pformat(opts)))
  


if __name__ == '__main__':
  main(sys.argv )

