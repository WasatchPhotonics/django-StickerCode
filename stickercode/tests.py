""" unit and functional tests for sticker code creation and web service
wrapper.
"""

import os
import sys
import logging
import unittest

from pyramid import testing

from webtest import TestApp, Upload

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

    def test_deform_display(self):
        from stickercode.views import LabelViews
        request = testing.DummyRequest()
        inst = LabelViews(request)
        result = inst.deform_view()

        appstruct = result["appstruct"]
        self.assertEqual(appstruct.serial, "deformnull")
       
class FunctionalTests(unittest.TestCase):
    def setUp(self):
        from stickercode import main
        settings = {}
        app = main({}, **settings)
        self.testapp = TestApp(app)

    def tearDown(self):
        del self.testapp

    def test_deform_display_not_submitted(self):
        res = self.testapp.get("/deform_view")
        log.info("deform res: %s", res)
        self.assertEqual(res.status_code, 200)

        form = res.forms["deform"]
        self.assertTrue(form["serial"].value, "deformnull")

    def test_deform_display_bad_submit(self):
        res = self.testapp.get("/deform_view")

 
if __name__ == "__main__":
    unittest.main()
