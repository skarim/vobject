import vobject

from vobject import base, icalendar, vcard

import doctest, test_vobject, unittest

base.logger.setLevel(base.logging.FATAL)
#------------------- Testing and running functions -----------------------------
# named additional_tests for setuptools
def additional_tests():

    flags = doctest.NORMALIZE_WHITESPACE | doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS
    suite = unittest.TestSuite()
    for module in test_vobject, icalendar, vobject, vcard:
        suite.addTest(doctest.DocTestSuite(module, optionflags=flags))

    suite.addTest(doctest.DocFileSuite(
        'README.md', 'test_files/more_tests.txt',
        package='__main__', optionflags=flags
    ))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    unittest.main(testRunner=runner)



vcardtest =r"""BEGIN:VCARD
VERSION:3.0
FN:Daffy Duck Knudson (with Bugs Bunny and Mr. Pluto)
N:Knudson;Daffy Duck (with Bugs Bunny and Mr. Pluto)
NICKNAME:gnat and gnu and pluto
BDAY;value=date:02-10
TEL;type=HOME:+01-(0)2-765.43.21
TEL;type=CELL:+01-(0)5-555.55.55
ACCOUNT;type=HOME:010-1234567-05
ADR;type=HOME:;;Haight Street 512\;\nEscape\, Test;Novosibirsk;;80214;Gnuland
TEL;type=HOME:+01-(0)2-876.54.32
ORG:University of Novosibirsk\, Department of Octopus
  Parthenogenesis
END:VCARD"""

vcardWithGroups = r"""home.begin:vcard
version:3.0
source:ldap://cn=Meister%20Berger,o=Universitaet%20Goerlitz,c=DE
name:Meister Berger
fn:Meister Berger
n:Berger;Meister
bday;value=date:1963-09-21
o:Universit=E6t G=F6rlitz
title:Mayor
title;language=de;value=text:Burgermeister
note:The Mayor of the great city of
  Goerlitz in the great country of Germany.\nNext line.
email;internet:mb@goerlitz.de
home.tel;type=fax,voice;type=msg:+49 3581 123456
home.label:Hufenshlagel 1234\n
 02828 Goerlitz\n
 Deutschland
END:VCARD"""

lowercaseComponentNames = r"""begin:vcard
fn:Anders Bobo
n:Bobo;Anders
org:Bobo A/S;Vice President, Technical Support
adr:Rockfeller Center;;Mekastreet;Bobocity;;2100;Myworld
email;internet:bobo@example.com
tel;work:+123455
tel;fax:+123456
tel;cell:+123457
x-mozilla-html:FALSE
url:http://www.example.com
version:2.1
end:vcard"""

icalWeirdTrigger = r"""BEGIN:VCALENDAR
CALSCALE:GREGORIAN
X-WR-TIMEZONE;VALUE=TEXT:US/Pacific
METHOD:PUBLISH
PRODID:-//Apple Computer\, Inc//iCal 1.0//EN
X-WR-CALNAME;VALUE=TEXT:Example
VERSION:2.0
BEGIN:VEVENT
DTSTART:20021028T140000Z
BEGIN:VALARM
TRIGGER:20021028T120000Z
ACTION:DISPLAY
DESCRIPTION:This trigger is a date-time without a VALUE=DATE-TIME parameter
END:VALARM
END:VEVENT
END:VCALENDAR"""


__test__ = { "Test readOne" :
    r"""
    >>> s3 = StringIO('cn:Babs Jensen\r\ncn:Barbara J Jensen\r\nsn:Jensen\r\nemail:babs@umich.edu\r\nphone:+1 313 747-4454\r\nx-id:1234567890\r\n')
    >>> ex1 = base.readOne(s3, findBegin=False)
    >>> ex1
    <*unnamed*| [<CN{}Babs Jensen>, <CN{}Barbara J Jensen>, <EMAIL{}babs@umich.edu>, <PHONE{}+1 313 747-4454>, <SN{}Jensen>, <X-ID{}1234567890>]>
    >>> ex1.serialize()
    'CN:Babs Jensen\r\nCN:Barbara J Jensen\r\nEMAIL:babs@umich.edu\r\nPHONE:+1 313 747-4454\r\nSN:Jensen\r\nX-ID:1234567890\r\n'
    """,

    "ical trigger workaround" :
    """

    >>> badical = base.readOne(icalWeirdTrigger)
    >>> badical.vevent.valarm.description.value
    u'This trigger is a date-time without a VALUE=DATE-TIME parameter'
    >>> badical.vevent.valarm.trigger.value
    datetime.datetime(2002, 10, 28, 12, 0, tzinfo=tzutc())
    """,

    "Generate UIDs automatically test:" :

    """
    >>> import datetime
    >>> cal = base.newFromBehavior('vcalendar')
    >>> cal.add('vevent').add('dtstart').value = datetime.datetime(2006,2,2,10)
    >>> ser = cal.serialize()
    >>> len(cal.vevent.uid_list)
    1
    """,

    "VCARD 3.0 parse test:" :

    r"""
    >>> card = base.readOne(vcardtest)
    >>> card.adr.value
    <Address: Haight Street 512;\nEscape, Test\nNovosibirsk,  80214\nGnuland>
    >>> print(card.adr.value)
    Haight Street 512;
    Escape, Test
    Novosibirsk,  80214
    Gnuland
    >>> card.org.value
    [u'University of Novosibirsk, Department of Octopus Parthenogenesis']
    >>> print(card.serialize())
    BEGIN:VCARD
    VERSION:3.0
    ACCOUNT;TYPE=HOME:010-1234567-05
    ADR;TYPE=HOME:;;Haight Street 512\;\nEscape\, Test;Novosibirsk;;80214;Gnul
     and
    BDAY;VALUE=date:02-10
    FN:Daffy Duck Knudson (with Bugs Bunny and Mr. Pluto)
    N:Knudson;Daffy Duck (with Bugs Bunny and Mr. Pluto);;;
    NICKNAME:gnat and gnu and pluto
    ORG:University of Novosibirsk\, Department of Octopus Parthenogenesis
    TEL;TYPE=HOME:+01-(0)2-765.43.21
    TEL;TYPE=CELL:+01-(0)5-555.55.55
    TEL;TYPE=HOME:+01-(0)2-876.54.32
    END:VCARD
    """,

    "Multi-text serialization test:" :

    """
    >>> category = base.newFromBehavior('categories')
    >>> category.value = ['Random category']
    >>> print(category.serialize().strip())
    CATEGORIES:Random category
    >>> category.value.append('Other category')
    >>> print(category.serialize().strip())
    CATEGORIES:Random category,Other category
    """,

    "Semi-colon separated multi-text serialization test:" :

    """
    >>> requestStatus = base.newFromBehavior('request-status')
    >>> requestStatus.value = ['5.1', 'Service unavailable']
    >>> print(requestStatus.serialize().strip())
    REQUEST-STATUS:5.1;Service unavailable
    """,

    "vCard groups test:" :

    """
    >>> card = base.readOne(vcardWithGroups)
    >>> card.group
    u'home'
    >>> card.tel.group
    u'home'
    >>> card.group = card.tel.group = 'new'
    >>> card.tel.serialize().strip()
    'new.TEL;TYPE=fax,voice,msg:+49 3581 123456'
    >>> card.serialize().splitlines()[0]
    'new.BEGIN:VCARD'
    >>> dtstart = base.newFromBehavior('dtstart')
    >>> dtstart.group = "badgroup"
    >>> dtstart.serialize()
    Traceback (most recent call last):
    ...
    VObjectError: "<DTSTART{}> has a group, but this object doesn't support groups"
    """,

    "Lowercase components test:" :

    """
    >>> card = base.readOne(lowercaseComponentNames)
    >>> card.version
    <VERSION{}2.1>
    """,

    "Default behavior test" :

    """
    >>> card = base.readOne(vcardWithGroups)
    >>> base.getBehavior('note') == None
    True
    >>> card.note.behavior
    <class 'vobject.vcard.VCardTextBehavior'>
    >>> print(card.note.value)
    The Mayor of the great city of  Goerlitz in the great country of Germany.
    Next line.
    """
    }
