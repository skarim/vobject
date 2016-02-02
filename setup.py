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
   - Python 3 compatible
   - Updated version of dateutil (2.4.0)
   - More comprehensive unit tests available in tests.py
   - Performance improvements in iteration
   - Test files are included in PyPI download package

For older changes, see
   - http://eventable.github.io/vobject/#release-history or
   - http://vobject.skyhouseconsulting.com/history.html
"""

from setuptools import setup, find_packages

doclines = __doc__.splitlines()

setup(name = "vobject",
      version = "0.9.0",
      author = "Jeffrey Harris",
      author_email = "jeffrey@osafoundation.org",
      maintainer = "Sameen Karim",
      maintainer_email="sameen@eventable.com",
      license = "Apache",
      zip_safe = True,
      url = "http://eventable.github.io/vobject/",
      entry_points = {
            'console_scripts': [
                  'ics_diff = vobject.ics_diff:main',
                  'change_tz = vobject.change_tz:main'
            ]
      },
      include_package_data = True,
      install_requires = ['python-dateutil == 2.4.0'],
      platforms = ["any"],
      packages = find_packages(),
      description = doclines[0],
      long_description = "\n".join(doclines[2:]),
      classifiers =  """
      Development Status :: 5 - Production/Stable
      Environment :: Console
      License :: OSI Approved :: Apache Software License
      Intended Audience :: Developers
      Natural Language :: English
      Programming Language :: Python
      Operating System :: OS Independent
      Topic :: Text Processing""".strip().splitlines()
      )
