import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "insulaudit",
    version = "0.0.1",
    author = "Ben West",
    author_email = "bewest@gmail.com",
    description = ("Audit insulin therapy.  Increase fidelity of care."),
    license = "BSD",
    url = "http://github.com/bewest/insulaudit",
    packages=find_packages('src'),
    long_description=read('README'),
)

#####
# EOF
