""" unit and functional tests for sticker code creation and web service
wrapper.
"""

import os
import sys
import shutil
import logging
import unittest

from slugify import slugify

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

    def test_length_within_range(self):
        from stickercode.stickergenerator import QL700Label
        filename = "dontexist.png"
        touch_erase(filename)

        fail_domain = "superlongdomainnametotriggerfailures"
        self.assertRaises(TypeError, QL700Label, domain=fail_domain)

        fail_serial = "aserialnumberthatiswaytoolongtotriggerfailures"
        self.assertRaises(TypeError, QL700Label, serial=fail_serial)

class TestStickerCodeViews(unittest.TestCase):
    def setUp(self):
        self.clean_test_files()
        self.config = testing.setUp()

    def tearDown(self):
        # Comment out this line for easier post-test state inspections
        #self.clean_test_files()
        testing.tearDown()

    def clean_test_files(self):
        # Remove the directory if it exists
        test_serials = ["FT1234", "UT5555", "UT0001"]

        for item in test_serials:
            dir_out = "database/%s" % slugify(item)
            if os.path.exists(dir_out):
                result = shutil.rmtree(dir_out)
                self.assertIsNone(result)

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

    def test_post_invalid_data(self):
        from stickercode.views import LabelViews

        test_serial = ""
        new_dict = {"submit":"True", "serial":test_serial}
        request = testing.DummyRequest(new_dict)
        inst = LabelViews(request)
        result = inst.qr_label()

        data = result["data"]
        self.assertEqual(data.serial, test_serial)

    def test_serialless_route_to_placeholder(self):
        from stickercode.views import LabelViews

        # If the blank_label view is requested, always return
        # placeholder file
        request = testing.DummyRequest()
        inst = LabelViews(request)
        result = inst.blank_label()
        
        self.assertEqual(result.content_length, 32743)

    def test_view_unknown_serial_returns_placeholder(self):
        from stickercode.views import LabelViews

        # No serial should raise exception
        request = testing.DummyRequest()
        inst = LabelViews(request)
        self.assertRaises(KeyError, inst.show_label) 

        # If the specified serial is blank or not found, return the
        # placeholder image
        request = testing.DummyRequest()
        request.matchdict["serial"] = ""
        inst = LabelViews(request)
        result = inst.show_label()
        
        self.assertEqual(result.content_length, 32743)

    def test_view_known_generated_label(self):
        from stickercode.views import LabelViews
        
        # copy a known image into the database folder, make sure the get
        # sizes match

        test_serial = slugify("UT5555")
        dir_out = "database/%s/" % test_serial
       
        os.makedirs(dir_out)
        
        source_file = "resources/known_example.png"
        dest_file = "%s/label.png" % dir_out

        shutil.copy(source_file, dest_file) 
        self.assertTrue(os.path.exists(dest_file))
        
        request = testing.DummyRequest()
        request.matchdict["serial"] = test_serial
        inst = LabelViews(request)
        result = inst.show_label()
        
        self.assertEqual(result.content_length, 39610)
        
    def test_post_generates_label_in_database(self):
        from stickercode.views import LabelViews
    
        # POST to create a qr file, verify it exists on the disk
        test_serial = "UT0001" 
        new_dict = {"submit":"True", "serial":test_serial} 
        request = testing.DummyRequest(new_dict)
        inst = LabelViews(request)
        result = inst.qr_label()

        slug_serial = slugify(test_serial)
        dest_file = "database/%s/label.png" % slug_serial
        self.assertTrue(os.path.exists(dest_file))
        self.assertEqual(os.path.getsize(dest_file), 15079)

        # verify the view returns it
        request = testing.DummyRequest()
        request.matchdict["serial"] = test_serial
        inst = LabelViews(request)
        result = inst.show_label()
        self.assertEqual(result.content_length, 15079)
        
 
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
        self.assertEqual(res.status_code, 200)

        form = res.forms["deform"]
        self.assertEqual(form["serial"].value, "")

        self.assertTrue("src=\"/show_label" in res.body)

    def test_post_form_returns_populated_data(self):
        ft_serial = "FT7890"

        res = self.testapp.get("/qr_label")
        form = res.forms["deform"]
        form["serial"] = ft_serial

        submit_res = form.submit("submit")
        new_form = submit_res.forms["deform"]
        self.assertEqual(new_form["serial"].value, ft_serial)

        # Re-submit to make sure the directory is not overwritten for
        # coverage
        submit_res = form.submit("submit")
        new_form = submit_res.forms["deform"]
        self.assertEqual(new_form["serial"].value, ft_serial)
