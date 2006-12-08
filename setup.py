#!/usr/bin/env python
"""VObject: module for reading vCard and vCalendar files

Parses iCalendar and vCard files into Python data structures, decoding the relevant encodings. Also serializes vobject data structures to iCalendar, vCard, or (expirementally) hCalendar unicode strings.

Requires python 2.4 or later, dateutil (http://labix.org/python-dateutil) 1.1 or later.

Recent changes:
- Added ignoreUnreadable flag to readOne and readComponents
- Tolerate date-time or date fields incorrectly failing to set VALUE=DATE for date values
- Cause unrecognized lines to default to use a text behavior, so commas, carriage returns, and semi-colons are escaped properly in unrecognized lines

For older changes, see http://vobject.skyhouseconsulting.com/history.html or http://websvn.osafoundation.org/listing.php?repname=vobject&path=/trunk/

"""

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

#from distutils.core import setup

# Metadata
PACKAGE_NAME = "vobject"
PACKAGE_VERSION = "0.4.5"

ALL_EXTS = ['*.py', '*.ics', '*.txt']

packages = ['vobject']

doclines = __doc__.splitlines()

setup(name = "vobject",
      version = PACKAGE_VERSION,
      author = "Jeffrey Harris",
      author_email = "jeffrey@osafoundation.org",
      license = "Apache",
      zip_safe = True,
      url = "http://vobject.skyhouseconsulting.com",

      package_dir = {'':'src'},
      package_data = {'': ALL_EXTS},

      install_requires = ['python-dateutil >= 1.1'], 

      platforms = ["any"],
      packages = ["vobject"],
      description = doclines[0],
      long_description = "\n".join(doclines[2:]),
      classifiers =  """
      Development Status :: 4 - Beta
      Environment :: Console
      License :: OSI Approved :: BSD License
      Intended Audience :: Developers
      Natural Language :: English
      Programming Language :: Python
      Operating System :: OS Independent
      Topic :: Text Processing""".strip().splitlines()
      )
