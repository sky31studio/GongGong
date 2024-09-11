from unittest import TestCase

from xtu_ems.util import ImageDetector


class TestImageDetector(TestCase):
    def test_verify(self):
        with open('./verifycode.jpeg', 'rb') as f:
            img = f.read()
        res = ImageDetector().verify(img)
        self.assertEqual('cnbz', res)
