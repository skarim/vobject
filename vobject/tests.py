import unittest

from pkg_resources import resource_stream
from six import StringIO

from vobject.base import readComponents


def get_stream(path):
    """
    Helper function to open test files.
    """
    try:
        return resource_stream(__name__, 'test_files/' + path)
    except Exception:
        return resource_stream(__name__, path)


class TestVobject(unittest.TestCase):

    def setUp(self):
        self.simple_test_cal = get_stream("simple_test.ics")

    def test_readComponents(self):
        f = StringIO(self.simple_test_cal)
        cal = next(readComponents(f))

        self.assertEqual(cal, "<VCALENDAR| [<VEVENT| [<SUMMARY{u'BLAH': [u'hi!']}Bastille Day Party>]>]>")
        self.assertEqual(cal.vevent.summary, "<SUMMARY{u'BLAH': [u'hi!']}Bastille Day Party>")


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
