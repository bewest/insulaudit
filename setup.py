import os
import sys
from setuptools import setup, find_packages

"""
Setup script to install insulaudit.

# sudo python setup.py develop # to hack
# sudo python setup.py install # permanent

"""

src = 'src'
sys.path.append(src)
import insulaudit.version as insulaudit
version     = insulaudit.__version__
author      = insulaudit.__author__
description = insulaudit.__doc__
license     = insulaudit.__license__
# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name         = "insulaudit",
    version      = version,
    author       = author,
    author_email = "bewest@gmail.com",
    description  = description,
    license      = license,
    url          = "http://github.com/bewest/insulaudit",
    packages     = find_packages(src),
    package_dir  = { '': src },
    install_requires=[ 'pyserial', 'pyCLI', 'numpy', 'python-dateutil', 'doctest' ],
    long_description=read('README'),
    entry_points = {
      'console_scripts': [ 'insulaudit = insulaudit.main:main' ] },
)

#####
# EOF
