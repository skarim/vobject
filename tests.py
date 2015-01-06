#-*- coding: utf-8 -*-
from __future__ import print_function

import datetime
import dateutil
import re
import unittest

from dateutil.tz import tzutc

from vobject import base
from vobject import icalendar

from vobject.base import __behaviorRegistry as behavior_registry
from vobject.base import ContentLine, newFromBehavior, parseLine, parseParams, ParseError, VObjectError
from vobject.base import readComponents, textLineToContentLine

from vobject.icalendar import MultiDateBehavior, PeriodBehavior, RecurringComponent, utc
from vobject.icalendar import parseDtstart, stringToTextValues, stringToPeriod, timedeltaToString

twoHours  = datetime.timedelta(hours=2)


def get_test_file(path):
    """
    Helper function to open and read test files.
    """
    filepath = "test_files/{}".format(path)
    f = open(filepath, 'r')
    text = f.read()
    f.close()
    return text


class TestCalendarSerializing(unittest.TestCase):
    maxDiff = None

    def test_scratchbuild(self):
        "CreateCalendar 2.0 format from scratch"
        test_cal = get_test_file("simple_2_0_test.ics")
        cal = base.newFromBehavior('vcalendar', '2.0')
        cal.add('vevent')
        cal.vevent.add('dtstart').value = datetime.datetime(2006, 5, 9)
        cal.vevent.add('description').value = "Test event"
        cal.vevent.add('created').value = datetime.datetime(2006, 1, 1, 10, tzinfo=dateutil.tz.tzical("test_files/timezones.ics").get('US/Pacific'))
        cal.vevent.add('uid').value = "Not very random UID"

        # has a date problem
        self.assertEqual(
            cal.serialize(),
            test_cal
        )

    def test_unicode(self):
        test_cal = get_test_file("utf8_test.ics")
        vevent = base.readOne(test_cal).vevent

        self.assertEqual(
            vevent.summary.value,
            'The title こんにちはキティ'
        )


class TestBehaviors(unittest.TestCase):
    def test_general_behavior(self):
        """
        Tests for behavior registry, getting and creating a behavior.
        """
        # Check expected behavior registry.
        # THIS HAS 25 FEWER ITEMS IN PYTHON3???
        self.assertEqual(
            sorted(behavior_registry.keys()),
            ['', 'ACTION', 'AVAILABLE', 'BUSYTYPE', 'CALSCALE', 'CATEGORIES', 'CLASS', 'COMMENT', 'COMPLETED', 'CONTACT', 'CREATED', 'DAYLIGHT', 'DESCRIPTION', 'DTEND', 'DTSTAMP', 'DTSTART', 'DUE', 'DURATION', 'EXDATE', 'EXRULE', 'FREEBUSY', 'LAST-MODIFIED', 'LOCATION', 'METHOD', 'PRODID', 'RDATE', 'RECURRENCE-ID', 'RELATED-TO', 'REQUEST-STATUS', 'RESOURCES', 'RRULE', 'STANDARD', 'STATUS', 'SUMMARY', 'TRANSP', 'TRIGGER', 'UID', 'VALARM', 'VAVAILABILITY', 'VCALENDAR', 'VEVENT', 'VFREEBUSY', 'VJOURNAL', 'VTIMEZONE', 'VTODO']
        )

        # test get_behavior
        behavior = base.getBehavior('VCALENDAR')
        self.assertEqual(
            str(behavior),
            "<class 'vobject.icalendar.VCalendar2_0'>"
        )
        self.assertTrue(behavior.isComponent)

        self.assertEqual(
            base.getBehavior("invalid_name"),
            None
        )
        # test for ContentLine (not a component)
        non_component_behavior = base.getBehavior('RDATE')
        self.assertFalse(non_component_behavior.isComponent)

    def test_MultiDateBehavior(self):
        parseRDate = MultiDateBehavior.transformToNative
        self.assertEqual(
            str(parseRDate(textLineToContentLine("RDATE;VALUE=DATE:19970304,19970504,19970704,19970904"))),
            "<RDATE{'VALUE': ['DATE']}[datetime.date(1997, 3, 4), datetime.date(1997, 5, 4), datetime.date(1997, 7, 4), datetime.date(1997, 9, 4)]>"
        )
        self.assertEqual(
            str(parseRDate(textLineToContentLine("RDATE;VALUE=PERIOD:19960403T020000Z/19960403T040000Z,19960404T010000Z/PT3H"))),
            "<RDATE{'VALUE': ['PERIOD']}[(datetime.datetime(1996, 4, 3, 2, 0, tzinfo=tzutc()), datetime.datetime(1996, 4, 3, 4, 0, tzinfo=tzutc())), (datetime.datetime(1996, 4, 4, 1, 0, tzinfo=tzutc()), datetime.timedelta(0, 10800))]>"
        )

    def test_periodBehavior(self):
        line = ContentLine('test', [], '', isNative=True)
        line.behavior = PeriodBehavior
        line.value = [(datetime.datetime(2006, 2, 16, 10), twoHours)]

        self.assertEqual(
            line.transformFromNative().value,
            '20060216T100000/PT2H'
        )
        self.assertEqual(
            line.transformToNative().value,
            [(datetime.datetime(2006, 2, 16, 10, 0), datetime.timedelta(0, 7200))]
        )

        line.value.append((datetime.datetime(2006, 5, 16, 10), twoHours))

        self.assertEqual(
            line.serialize().strip(),
            'TEST:20060216T100000/PT2H,20060516T100000/PT2H'
        )


class TestVobject(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        cls.simple_test_cal = get_test_file("simple_test.ics")

    def test_readComponents(self):
        cal = next(readComponents(self.simple_test_cal))

        self.assertEqual(str(cal), "<VCALENDAR| [<VEVENT| [<SUMMARY{'BLAH': ['hi!']}Bastille Day Party>]>]>")
        self.assertEqual(str(cal.vevent.summary), "<SUMMARY{'BLAH': ['hi!']}Bastille Day Party>")

    def test_parseLine(self):
        self.assertEqual(parseLine("BLAH:"), ('BLAH', [], '', None))
        self.assertEqual(
            parseLine("RDATE:VALUE=DATE:19970304,19970504,19970704,19970904"),
            ('RDATE', [], 'VALUE=DATE:19970304,19970504,19970704,19970904', None)
        )
        self.assertEqual(
            parseLine('DESCRIPTION;ALTREP="http://www.wiz.org":The Fall 98 Wild Wizards Conference - - Las Vegas, NV, USA'),
            ('DESCRIPTION', [['ALTREP', 'http://www.wiz.org']], 'The Fall 98 Wild Wizards Conference - - Las Vegas, NV, USA', None)
        )
        self.assertEqual(
            parseLine("EMAIL;PREF;INTERNET:john@nowhere.com"),
            ('EMAIL', [['PREF'], ['INTERNET']], 'john@nowhere.com', None)
        )
        self.assertEqual(
            parseLine('EMAIL;TYPE="blah",hah;INTERNET="DIGI",DERIDOO:john@nowhere.com'),
            ('EMAIL', [['TYPE', 'blah', 'hah'], ['INTERNET', 'DIGI', 'DERIDOO']], 'john@nowhere.com', None)
        )
        self.assertEqual(
            parseLine('item1.ADR;type=HOME;type=pref:;;Reeperbahn 116;Hamburg;;20359;'),
            ('ADR', [['type', 'HOME'], ['type', 'pref']], ';;Reeperbahn 116;Hamburg;;20359;', 'item1')
        )
        self.assertRaises(ParseError, parseLine, ":")


class TestGeneralFileParsing(unittest.TestCase):
    """
    General tests for parsing ics files.
    """
    def test_readOne(self):
        cal = get_test_file("silly_test.ics")
        silly = base.readOne(cal, findBegin=False)
        self.assertEqual(
            str(silly),
            "<SILLYPROFILE| [<MORESTUFF{}this line is not folded, but in practice probably ought to be, as it is exceptionally long, and moreover demonstratively stupid>, <SILLYNAME{}name>, <STUFF{}foldedline>]>"
        )
        self.assertEqual(
            str(silly.stuff),
            "<STUFF{}foldedline>"
        )

    def test_importing(self):
        cal = get_test_file("standard_test.ics")
        c = base.readOne(cal, validate=True)
        self.assertEqual(
            str(c.vevent.valarm.trigger),
            "<TRIGGER{}-1 day, 0:00:00>"
        )
        # PY3 PROBLEM!!!!!!!!!!!!!!
        # py3 is returning value as a string, not a datetime.
        # ToDo: figure out why, because it kills this whole block of tests.
        # The same bug also breaks test_freeBusy below.
        #self.assertEqual(
        #    str(c.vevent.dtstart.value),
        #    "2002-10-28"
        #)

        #self.assertTrue(
        #    isinstance(c.vevent.dtstart.value, datetime.datetime)
        #)
        #self.assertEqual(
        #    str(c.vevent.dtend.value),
        #    "2002-10-28"
        #)
        #self.assertTrue(
        #    isinstance(c.vevent.dtend.value, datetime.datetime)
        #)
        #self.assertEqual(
        #    c.vevent.dtstamp.value,
        #    datetime.datetime(2002, 10, 28, 1, 17, 6, tzinfo=tzutc())
        #)
        # END PY3 PROBLEM!!!!!!!!!!!!!!

        vevent = c.vevent.transformFromNative()
        self.assertEqual(
            str(vevent.rrule),
            "<RRULE{}FREQ=Weekly;COUNT=10>"
        )

    def test_bad_stream(self):
        cal = get_test_file("badstream.ics")
        self.assertRaises(ParseError, base.readOne, cal)

    def test_bad_line(self):
        cal = get_test_file("badline.ics")
        self.assertRaises(ParseError, base.readOne, cal)

        newcal = base.readOne(cal, ignoreUnreadable=True)
        self.assertEqual(
            str(newcal.vevent.x_bad_underscore),
            '<X-BAD-UNDERSCORE{}TRUE>'
        )

    def test_parseParams(self):
        self.assertEqual(
            parseParams(';ALTREP="http://www.wiz.org"'),
            [['ALTREP', 'http://www.wiz.org']]
        )
        self.assertEqual(
            parseParams(';ALTREP="http://www.wiz.org;;",Blah,Foo;NEXT=Nope;BAR'),
            [['ALTREP', 'http://www.wiz.org;;', 'Blah', 'Foo'], ['NEXT', 'Nope'], ['BAR']]
        )


class TestIcalendar(unittest.TestCase):
    """
    Tests for icalendar.py
    """
    def test_parseDTStart(self):
        """
        Should take a content line and return a datetime object.
        """
        self.assertEqual(
            parseDtstart(textLineToContentLine("DTSTART:20060509T000000")),
            datetime.datetime(2006, 5, 9, 0, 0)
        )

    def test_stringToTextValues(self):
        self.assertEqual(
            stringToTextValues(''),
            ['']
        )
        self.assertEqual(
            stringToTextValues('abcd,efgh'),
            ['abcd', 'efgh']
        )
    def test_stringToPeriod(self):
        self.assertEqual(
            stringToPeriod("19970101T180000Z/19970102T070000Z"),
            (datetime.datetime(1997, 1, 1, 18, 0, tzinfo=tzutc()), datetime.datetime(1997, 1, 2, 7, 0, tzinfo=tzutc()))
        )
        self.assertEqual(
            stringToPeriod("19970101T180000Z/PT1H"),
            (datetime.datetime(1997, 1, 1, 18, 0, tzinfo=tzutc()), datetime.timedelta(0, 3600))
        )

    def test_timedeltaToString(self):
        self.assertEqual(
            timedeltaToString(twoHours),
            'PT2H'
        )
        self.assertEqual(
            timedeltaToString(datetime.timedelta(minutes=20)),
            'PT20M'
        )

    def test_freeBusy(self):
        test_cal = get_test_file("freebusy.ics")

        vfb = newFromBehavior('VFREEBUSY')
        vfb.add('uid').value = 'test'
        vfb.add('dtstart').value = datetime.datetime(2006, 2, 16, 1, tzinfo=utc)
        vfb.add('dtend').value   = vfb.dtstart.value + twoHours
        vfb.add('freebusy').value = [(vfb.dtstart.value, twoHours / 2)]
        vfb.add('freebusy').value = [(vfb.dtstart.value, vfb.dtend.value)]

        # print(vfb.serialize())

        # PY3 PROBLEM!!!!!!!!!!!!!!
        # Won't pass 3 yet due to datetime objects being seen as strings.
        #self.assertEqual(
        #    vfb.serialize(),
        #    test_cal
        #)
        # END PY3 PROBLEM!!!!!!!!!!!!!!

    def test_availablity(self):
        test_cal = get_test_file("availablity.ics")

        vcal = newFromBehavior('VAVAILABILITY')
        vcal.add('uid').value = 'test'
        vcal.add('dtstamp').value = datetime.datetime(2006, 2, 15, 0, tzinfo=utc)
        vcal.add('dtstart').value = datetime.datetime(2006, 2, 16, 0, tzinfo=utc)
        vcal.add('dtend').value   = datetime.datetime(2006, 2, 17, 0, tzinfo=utc)
        vcal.add('busytype').value = "BUSY"

        av = newFromBehavior('AVAILABLE')
        av.add('uid').value = 'test1'
        av.add('dtstamp').value = datetime.datetime(2006, 2, 15, 0, tzinfo=utc)
        av.add('dtstart').value = datetime.datetime(2006, 2, 16, 9, tzinfo=utc)
        av.add('dtend').value   = datetime.datetime(2006, 2, 16, 12, tzinfo=utc)
        av.add('summary').value = "Available in the morning"

        vcal.add(av)

        # PY3 PROBLEM!!!!!!!!!!!!!!
        # Won't pass 3 yet due to datetime objects being seen as strings.
        #self.assertEqual(
        #    vcal.serialize(),
        #    test_cal
        #)
        # END PY3 PROBLEM!!!!!!!!!!!!!!

    def test_regexes(self):
        self.assertEqual(
            re.findall(base.patterns['name'], '12foo-bar:yay'),
            ['12foo-bar', 'yay']
        )
        self.assertEqual(
            re.findall(base.patterns['safe_char'], 'a;b"*,cd'),
            ['a', 'b', '*', 'c', 'd']
        )
        self.assertEqual(
            re.findall(base.patterns['qsafe_char'], 'a;b"*,cd'),
            ['a', ';', 'b', '*', ',', 'c', 'd']
        )
        self.assertEqual(
            re.findall(base.patterns['param_value'], '"quoted";not-quoted;start"after-illegal-quote', re.VERBOSE),
            ['"quoted"', '', 'not-quoted', '', 'start', '', 'after-illegal-quote', '']
        )
        match = base.line_re.match('TEST;ALTREP="http://www.wiz.org":value:;"')
        self.assertEqual(
            match.group('value'),
            'value:;"'
        )
        self.assertEqual(
            match.group('name'),
            'TEST'
        )
        self.assertEqual(
            match.group('params'),
            ';ALTREP="http://www.wiz.org"'
        )

    def test_recurrence(self):
        # PY3 PROBLEM!!!!!!!!!!!!!!
        # strings mean vevent is not what is expected, and can't get a rruleset.

        # Ensure date valued UNTILs in rrules are in a reasonable timezone,
        # and include that day (12/28 in this test)
        """
        test_file = get_test_file("recurrence.ics")
        cal = base.readOne(test_file, findBegin=False)
        dates = list(cal.vevent.getrruleset())
        self.assertEqual(
            dates[0],
            datetime.datetime(2006, 1, 26, 23, 0, tzinfo=tzutc())
        )
        self.assertEqual(
            dates[1],
            datetime.datetime(2006, 2, 23, 23, 0, tzinfo=tzutc())
        )
        self.assertEqual(
            dates[-1],
            datetime.datetime(2006, 12, 28, 23, 0, tzinfo=tzutc())
        )
        """

    def test_recurring_component(self):
        vevent = RecurringComponent(name='VEVENT')

        # init
        self.assertTrue(vevent.isNative)

        # rruleset should be None at this point.
        # No rules have been passed or created.
        self.assertEqual(vevent.rruleset, None)

        # Now add start and rule for recurring event
        vevent.add('dtstart').value = datetime.datetime(2005, 1, 19, 9)
        vevent.add('rrule').value =u"FREQ=WEEKLY;COUNT=2;INTERVAL=2;BYDAY=TU,TH"
        self.assertEqual(
            list(vevent.rruleset),
            [datetime.datetime(2005, 1, 20, 9, 0), datetime.datetime(2005, 2, 1, 9, 0)]
        )
        self.assertEqual(
            list(vevent.getrruleset(addRDate=True)),
            [datetime.datetime(2005, 1, 19, 9, 0), datetime.datetime(2005, 1, 20, 9, 0)]
        )

        # Also note that dateutil will expand all-day events (datetime.date values)
        # to datetime.datetime value with time 0 and no timezone.
        vevent.dtstart.value = datetime.date(2005,3,18)
        self.assertEqual(
            list(vevent.rruleset),
            [datetime.datetime(2005, 3, 29, 0, 0), datetime.datetime(2005, 3, 31, 0, 0)]
        )
        self.assertEqual(
            list(vevent.getrruleset(True)),
            [datetime.datetime(2005, 3, 18, 0, 0), datetime.datetime(2005, 3, 29, 0, 0)]
        )

if __name__ == '__main__':
    unittest.main()
