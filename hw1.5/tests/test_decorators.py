import unittest
from decorators import get_slug


class CacheDecoratorTestCase(unittest.TestCase):
    def test_get_slug(self):
        self.assertEqual(get_slug("Don't Give Up"), "don-t-give-up")
        self.assertEqual(
            get_slug("In the mirror, fall away"), "in-the-mirror-fall-away"
        )
        self.assertEqual(
            get_slug("- -1 23 12  bad text$#@#"), "1-23-12-bad-text"
        )
