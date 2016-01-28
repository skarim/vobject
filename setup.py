"""VObject: module for reading vCard and vCalendar files

Description
-----------

Parses iCalendar and vCard files into Python data structures, decoding the relevant encodings. Also serializes vobject data structures to iCalendar, vCard, or (experimentally) hCalendar unicode strings.

Requirements
------------

Requires python 2.4 or later, dateutil (http://labix.org/python-dateutil) 1.1 or later.

Recent changes
--------------
   - Make change_tz.py compatible with python 2.4, so the entire package stays compatible
   - Fall back to default (the most recent standard) behavior if a VCARD
     or VCALENDAR doesn't have a recognized VERSION
   - Fixed a bad performance bug when parsing large text bodies, thanks to Morgen Sagen at Apple
   - Changed license to Apache 2.0 from Apache 1.1
   - Worked around an issue with Apple Address Book's vcard PHOTO parser
   - Added change_tz module and script for quickly changing event timezones for an
     ics file.  Requires PyICU.
   - Add support for BYMONTHDAY=-1 (days before the end of the month) when setting rrules
     from a dateutil rrule
   - Tolerate a Ruby iCalendar library escaping semi-colons in RRULEs
   - Make vobjects pickle-able
   - Add introspection help for IPython so tab completion works with
     vobject's custom __getattr__
   - Allow Outlook's technically illegal use of commas in TZIDs
   - Allow unicode names for TZIDs
   - Worked around Lotus Notes use of underscores in names by just silently replacing
     with dashes
   - When allowing quoted-printable data, honor CHARSET for each line, defaulting to
     iso-8859-1
   - Simplified directory layout, unit tests are now available via setup.py test

For older changes, see
   - http://vobject.skyhouseconsulting.com/history.html or
   - http://websvn.osafoundation.org/listing.php?repname=vobject&path=/trunk/

"""

from setuptools import setup, find_packages

doclines = __doc__.splitlines()

setup(name = "vobject",
      version = "0.8.2",
      author = "Jeffrey Harris",
      author_email = "jeffrey@osafoundation.org",
      maintainer = "Sameen Karim",
      maintainer_email="sameen@eventable.com",
      license = "Apache",
      zip_safe = True,
      url = "http://eventable.github.io/vobject/",
      entry_points = { 'console_scripts': ['ics_diff = vobject.ics_diff:main',
                                           'change_tz = vobject.change_tz:main']},
      include_package_data = True,
      test_suite = "test_vobject",

      install_requires = ['python-dateutil >= 1.1'],

      platforms = ["any"],
      packages = find_packages(),
      description = doclines[0],
      long_description = "\n".join(doclines[2:]),
      classifiers =  """
      Development Status :: 5 - Production/Stable
      Environment :: Console
      License :: OSI Approved :: BSD License
      Intended Audience :: Developers
      Natural Language :: English
      Programming Language :: Python
      Operating System :: OS Independent
      Topic :: Text Processing""".strip().splitlines()
      )
