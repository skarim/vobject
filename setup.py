"""
VObject: module for reading vCard and vCalendar files

Description
-----------

Parses iCalendar and vCard files into Python data structures, decoding the
relevant encodings. Also serializes vobject data structures to iCalendar, vCard,
or (experimentally) hCalendar unicode strings.

Requirements
------------

Requires python 2.7 or later, dateutil 2.4.0 or later.

Recent changes
--------------
   - Improved PEP8 compliance
   - Improved Python 3 compatibility
   - Improved encoding/decoding
   - Correct handling of pytz timezones
   - Added tests.py to the PyPi package

For older changes, see
   - http://eventable.github.io/vobject/#release-history or
   - http://vobject.skyhouseconsulting.com/history.html
"""

from setuptools import setup, find_packages

doclines = (__doc__ or '').splitlines()

setup(name = "vobject",
      version = "0.9.4",
      author = "Jeffrey Harris",
      author_email = "jeffrey@osafoundation.org",
      maintainer = "Sameen Karim",
      maintainer_email="sameen@eventable.com",
      license = "Apache",
      zip_safe = True,
      url = "http://eventable.github.io/vobject/",
      download_url = 'https://github.com/eventable/vobject/tarball/0.9.4',
      bugtrack_url = "https://github.com/eventable/vobject/issues",
      entry_points = {
            'console_scripts': [
                  'ics_diff = vobject.ics_diff:main',
                  'change_tz = vobject.change_tz:main'
            ]
      },
      include_package_data = True,
      install_requires = ['python-dateutil >= 2.4.0'],
      platforms = ["any"],
      packages = find_packages(),
      description = "A full-featured Python package for parsing and creating "
                    "iCalendar and vCard files",
      long_description = "\n".join(doclines[2:]),
      keywords = ['vobject', 'icalendar', 'vcard', 'ics', 'vcs', 'hcalendar'],
      classifiers =  """
      Development Status :: 5 - Production/Stable
      Environment :: Console
      Intended Audience :: Developers
      License :: OSI Approved :: Apache Software License
      Natural Language :: English
      Operating System :: OS Independent
      Programming Language :: Python
      Programming Language :: Python :: 2.7
      Programming Language :: Python :: 3
      Topic :: Text Processing""".strip().splitlines()
      )
