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

        data = result["data"]

        self.assertEqual(data.serial, "")

    def test_post_returns_populated_data(self):
        from stickercode.views import LabelViews
  
        test_serial = "FT1234" 
        new_dict = {"submit":"True", "serial":test_serial} 
        request = testing.DummyRequest(new_dict)
        inst = LabelViews(request)
        result = inst.qr_label()

        data = result["data"]
        self.assertEqual(data.serial, test_serial)

       
class FunctionalTests(unittest.TestCase):
    def setUp(self):
        from stickercode import main
        settings = {}
        app = main({}, **settings)
        self.testapp = TestApp(app)

    def tearDown(self):
        del self.testapp

    def test_get_form_view(self):
        res = self.testapp.get("/qr_label")
        #log.info("label form res: %s", res)
        self.assertEqual(res.status_code, 200)

        form = res.forms["deform"]
        self.assertEqual(form["serial"].value, "")

    def test_post_form_returns_populated_data(self):
        ft_serial = "FT7890"

        res = self.testapp.get("/qr_label")
        form = res.forms["deform"]
        form["serial"] = ft_serial

        submit_res = form.submit("submit")
        #log.info("post submit: %s", submit_res)
        new_form = submit_res.forms["deform"]
        self.assertEqual(new_form["serial"].value, ft_serial)

 
if __name__ == "__main__":
    unittest.main()
