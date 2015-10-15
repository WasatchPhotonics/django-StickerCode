""" unit and functional tests for sticker code creation and web service
wrapper.
"""

import os
import sys
import logging
import unittest

from pyramid import testing

from stickercode.coverage_utils import touch_erase

log = logging.getLogger()
log.setLevel(logging.INFO)

strm = logging.StreamHandler(sys.stderr)
frmt = logging.Formatter("%(name)s - %(levelname)s %(message)s")
strm.setFormatter(frmt)
log.addHandler(strm)

class TestStickerGenerator(unittest.TestCase):
    def test_all_options_unrequired(self):
        from stickercode.stickergenerator import QL700Label
        filename = "ql700_label.png"
        touch_erase(filename)

        lbl = QL700Label()
        actual_size = os.path.getsize(filename)
        self.assertEqual(actual_size, 15858)

class TestStickerCodeViews(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_get_returns_empty_form(self):
        from stickercode.views import LabelViews

        request = testing.DummyRequest()
        inst = LabelViews(request)
        result = inst.qr_label()

        fields = result["fields"]

        self.assertEqual(fields.serial, "changetonull")
        
if __name__ == "__main__":
    unittest.main()
