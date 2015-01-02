from __future__ import print_function

import datetime
import unittest

from vobject.base import readComponents, parseLine, parseParams, ParseError
from vobject.icalendar import RecurringComponent

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


class TestRecurringComponent(unittest.TestCase):
    def test_recurring_component(self):
        vevent = RecurringComponent(name='VEVENT')

        # init
        self.assertTrue(vevent.isNative)
        vevent.add('rrule').value =u"FREQ=WEEKLY;COUNT=2;INTERVAL=2;BYDAY=TU,TH"
        vevent.add('dtstart').value = datetime.datetime(2005, 1, 19, 9)

        print('vevent.rruleset: ', vevent.rruleset)

        # When creating rrule's programmatically it should be kept in
        # mind that count doesn't necessarily mean what the spec says.
        #self.assertEqual(
        #    list(vevent.rruleset),
        #    [datetime.datetime(2005, 1, 20, 9, 0), datetime.datetime(2005, 2, 1, 9, 0)]
        #)
        #self.assertEqual(
        #    list(vevent.getrruleset(addRDate=True)),
        #    [datetime.datetime(2005, 1, 19, 9, 0), datetime.datetime(2005, 1, 20, 9, 0)]
        #)

        # Also note that dateutil will expand all-day events (datetime.date values)
        # to datetime.datetime value with time 0 and no timezone.
        vevent.dtstart.value = datetime.date(2005,3,18)

        print(list(vevent))

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
