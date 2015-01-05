from __future__ import print_function

import datetime
import dateutil
import unittest

from vobject.base import ContentLine, newFromBehavior, parseLine, parseParams, ParseError, readComponents, readOne
from vobject.icalendar import PeriodBehavior, RecurringComponent, utc, timedeltaToString

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


class TestVobject(unittest.TestCase):

    def setUp(self):
        self.simple_test_cal = get_test_file("simple_test.ics")

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

    def test_parseParams(self):
        self.assertEqual(
            parseParams(';ALTREP="http://www.wiz.org"'),
            [['ALTREP', 'http://www.wiz.org']]
        )
        self.assertEqual(
            parseParams(';ALTREP="http://www.wiz.org;;",Blah,Foo;NEXT=Nope;BAR'),
            [['ALTREP', 'http://www.wiz.org;;', 'Blah', 'Foo'], ['NEXT', 'Nope'], ['BAR']]
        )


class testGeneralFileParsing(unittest.TestCase):
    """
    General tests for parsing ics files.
    """
    def test_readOne(self):
        cal = get_test_file("silly_test.ics")
        silly = readOne(cal, findBegin=False)
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
        c = readOne(cal, validate=True)
        self.assertEqual(
            str(c.vevent.valarm.trigger),
            "<TRIGGER{}-1 day, 0:00:00>"
        )
        self.assertEqual(
            str(c.vevent.dtstart.value),
            "'2002-10-28 14:00:00-08:00'"
        )
        self.assertEqual(
            type(c.vevent.dtstart.value),
            "datetime"
        )
        self.assertEqual(
            str(c.vevent.dtend.value),
            datetime.datetime(2002, 10, 28, 15, 0, tzinfo=dateutil.tz.tzutc())
        )
        self.assertEqual(
            c.vevent.dtstamp.value,
            datetime.datetime(2002, 10, 28, 1, 17, 6, tzinfo=dateutil.tz.tzutc())
        )



        """
        >>> c.vevent.dtstamp.value
        datetime.datetime(2002, 10, 28, 1, 17, 6, tzinfo=tzutc())
        >>> c.vevent.valarm.description.value
        u'Event reminder, with comma\nand line feed'
        >>> c.vevent.valarm.description.serialize()
        'DESCRIPTION:Event reminder\\, with comma\\nand line feed\r\n'
        >>> vevent = c.vevent.transformFromNative()
        >>> vevent.rrule
        <RRULE{}FREQ=Weekly;COUNT=10>


        "Parsing tests" :

        >>> parseRDate = icalendar.MultiDateBehavior.transformToNative
        >>> icalendar.stringToTextValues('')
        ['']
        >>> icalendar.stringToTextValues('abcd,efgh')
        ['abcd', 'efgh']
        >>> icalendar.stringToPeriod("19970101T180000Z/19970102T070000Z")
        (datetime.datetime(1997, 1, 1, 18, 0, tzinfo=tzutc()), datetime.datetime(1997, 1, 2, 7, 0, tzinfo=tzutc()))
        >>> icalendar.stringToPeriod("19970101T180000Z/PT1H")
        (datetime.datetime(1997, 1, 1, 18, 0, tzinfo=tzutc()), datetime.timedelta(0, 3600))
        >>> parseRDate(base.textLineToContentLine("RDATE;VALUE=DATE:19970304,19970504,19970704,19970904"))
        <RDATE{'VALUE': ['DATE']}[datetime.date(1997, 3, 4), datetime.date(1997, 5, 4), datetime.date(1997, 7, 4), datetime.date(1997, 9, 4)]>
        >>> parseRDate(base.textLineToContentLine("RDATE;VALUE=PERIOD:19960403T020000Z/19960403T040000Z,19960404T010000Z/PT3H"))
        <RDATE{'VALUE': ['PERIOD']}[(datetime.datetime(1996, 4, 3, 2, 0, tzinfo=tzutc()), datetime.datetime(1996, 4, 3, 4, 0, tzinfo=tzutc())), (datetime.datetime(1996, 4, 4, 1, 0, tzinfo=tzutc()), datetime.timedelta(0, 10800))]>
        """


class testIcalendar(unittest.TestCase):
    """
    Tests for icalendar.py
    """

    def test_timedeltaToString(self):
        self.assertEqual(
            timedeltaToString(twoHours),
            'PT2H'
        )
        self.assertEqual(
            timedeltaToString(datetime.timedelta(minutes=20)),
            'PT20M'
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


    def test_freeBusy(self):
        test_cal = get_test_file("freebusy.ics")

        vfb = newFromBehavior('VFREEBUSY')
        vfb.add('uid').value = 'test'
        vfb.add('dtstart').value = datetime.datetime(2006, 2, 16, 1, tzinfo=utc)
        vfb.add('dtend').value   = vfb.dtstart.value + twoHours
        vfb.add('freebusy').value = [(vfb.dtstart.value, twoHours / 2)]
        vfb.add('freebusy').value = [(vfb.dtstart.value, vfb.dtend.value)]

        print(vfb.serialize())

        # Won't pass 3 yet due to datetime objects being seen as strings.
        #self.assertEqual(
        #    vfb.serialize(),
        #    test_cal
        #)

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

        # Won't pass 3 yet due to datetime objects being seen as strings.
        #self.assertEqual(
        #    vcal.serialize(),
        #    test_cal
        #)

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


    """def test_choice(self):
        element = random.choice(self.seq)
        self.assertTrue(element in self.seq)

    def test_sample(self):
        with self.assertRaises(ValueError):
            random.sample(self.seq, 20)
        for element in random.sample(self.seq, 5):
            self.assertTrue(element in self.seq)
    """

if __name__ == '__main__':
    unittest.main()
