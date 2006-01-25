#!/usr/bin/env python
"""VObject: module for reading vCard and vCalendar files

Parses iCalendar and vCard files into Python data structures, decoding the relevant encodings. Also serializes vobject data structures to valid iCalendar or vCard unicode strings.

Requires dateutil (https://moin.conectiva.com.br/DateUtil) 0.9 or later.
"""

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

doclines = __doc__.splitlines()

setup(name = "vobject",
      version = "0.2.3",
      author = "Jeffrey Harris",
      author_email = "jeffrey-osaf@skyhouseconsulting.com",
      license = "BSD",
      zip_safe = True
      url = "http://vobject.skyhouseconsulting.com",

      package_data = {'': ['*.py', '*.ics', '*.txt']},
      
      platforms = ["any"],
      packages = ["vobject"],
      description = doclines[0],
      long_description = "\n".join(doclines[2:]),
      classifiers =  """
      Development Status :: 3 - Alpha
      Environment :: Console
      License :: OSI Approved :: BSD License
      Intended Audience :: Developers
      Natural Language :: English
      Programming Language :: Python
      Operating System :: OS Independent
      Topic :: Text Processing""".strip().splitlines()
      )
