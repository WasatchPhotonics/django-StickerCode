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
from stickercode.coverage_utils import size_range, file_range

log = logging.getLogger()
log.setLevel(logging.INFO)

# Specify stdout as the logging output stream to reduce verbosity in the
# nosetest output. This will let you still see all of logging when
# running with python -u -m unittest, yet swallow it all in nosetest.
strm = logging.StreamHandler(sys.stdout)
frmt = logging.Formatter("%(name)s - %(levelname)s %(message)s")
strm.setFormatter(frmt)
log.addHandler(strm)

class TestCoverageUtils(unittest.TestCase):
    def test_file_does_not_exist(self):
        filename = "known_unknown_file"
        self.assertFalse(file_range(filename, 10000))

    def test_file_sizes_out_of_range(self):
        filename = "stickercode/assets/img/example_qr_label.png"
        # Too small with default range 50
        self.assertFalse(file_range(filename, 30000))
        # Too big
        self.assertFalse(file_range(filename, 33000))

class TestStickerGenerator(unittest.TestCase):
    def test_all_options_unrequired(self):
        from stickercode.stickergenerator import QL700Label
        filename = "ql700_label.png"
        touch_erase(filename)

        lbl = QL700Label()
        self.assertTrue(file_range(filename, 16098))

    def test_length_within_range(self):
        from stickercode.stickergenerator import QL700Label
        filename = "dontexist.png"
        touch_erase(filename)

        fail_domain = "superlongdomainnametotriggerfailures"
        self.assertRaises(TypeError, QL700Label, domain=fail_domain)

        fail_serial = "aserialnumberthatiswaytoolongtotriggerfailures"
        self.assertRaises(TypeError, QL700Label, serial=fail_serial)

    def test_with_parameters_returns_blob(self):
        from stickercode.stickergenerator import QL700Label
        filename = "ql700_label.png"
        touch_erase(filename)

        lbl = QL700Label(return_blob=True).return_blob()
    
        self.assertTrue(size_range(len(lbl), 16098, ok_range=500))


class DeformMockFieldStorage(object):
    """ Create a storage object that references a file for use in
    view unittests. Deform/colander requires a dictionary to address the
    multiple upload fields. This is not required for 'plain' html file
    uploads.
    """
    def __init__(self, source_file_name):
        self.filename = source_file_name
        self.file = file(self.filename)
        self.type = "file"
        self.length = os.path.getsize(self.filename)


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
            dir_out = "label_files/%s" % slugify(item)
            if os.path.exists(dir_out):
                shutil.rmtree(dir_out)

    def test_get_returns_default_form(self):
        from stickercode.views import LabelViews

        request = testing.DummyRequest()
        inst = LabelViews(request)
        result = inst.qr_label()
        self.assertIsNone(result.get("appstruct"))
        
    def test_serial_missing_or_empty_is_failure(self):
        from stickercode.views import LabelViews

        post_dict = {"submit":"submit"}
        request = testing.DummyRequest(post_dict)
        inst = LabelViews(request)
        result = inst.qr_label()
        self.assertIsNone(result.get("appstruct")) 

        post_dict = {"submit":"submit", "serial":""}
        request = testing.DummyRequest(post_dict)
        inst = LabelViews(request)
        result = inst.qr_label()
        self.assertIsNone(result.get("appstruct")) 

    def test_domain_missing_or_empty_is_failure(self):
        from stickercode.views import LabelViews

        post_dict = {"submit":"submit", "serial":"UT5555"}
        request = testing.DummyRequest(post_dict)
        inst = LabelViews(request)
        result = inst.qr_label()
        self.assertIsNone(result.get("appstruct")) 

        post_dict = {"submit":"submit", "serial":"UT5555",
                     "domain":""}
        request = testing.DummyRequest(post_dict)
        inst = LabelViews(request)
        result = inst.qr_label()
        self.assertIsNone(result.get("appstruct")) 

    def test_malformed_domain_is_failure(self):
        from stickercode.views import LabelViews

        bad_domains = ["http://", "http", "htt p://waspho.com", ".com"]
        for item in bad_domains:
            post_dict = {"submit":"submit", "serial":"UT5555",
                         "domain":item}
            request = testing.DummyRequest(post_dict)
            inst = LabelViews(request)
            result = inst.qr_label()
            self.assertIsNone(result.get("appstruct")) 


    def test_serial_and_domain_is_passing(self):
        from stickercode.views import LabelViews

        post_dict = {"submit":"submit", "serial":"UT5555",
                     "domain":"https://waspho.com"}
        request = testing.DummyRequest(post_dict)
        inst = LabelViews(request)
        result = inst.qr_label()
        self.assertIsNotNone(result.get("appstruct"))

    def test_post_with_image_creates_hardcoded_filename(self):
        from stickercode.views import LabelViews
    
        png_name = "resources/inverted_wasatch.png"
        png_file = DeformMockFieldStorage(png_name)
        png_upload_dict = {"upload":png_file}
 
        post_dict = {"submit":"submit", "serial":"UT5555",
                     "domain":"https://waspho.com",
                     "upload":png_upload_dict}
        request = testing.DummyRequest(post_dict)
        inst = LabelViews(request)
        result = inst.qr_label()
        
        dest_top = "label_files/ut5555/custom_background.png"
        self.assertTrue(file_range(dest_top, 63692))

    def test_post_fully_populated_creates_hardcoded_filename(self):
        from stickercode.views import LabelViews

        post_dict = {"submit":"submit", "serial":"UT5555",
                     "domain":"https://waspho.com"}
        request = testing.DummyRequest(post_dict)
        inst = LabelViews(request)
        result = inst.qr_label()
        
        dest_file = "label_files/ut5555/label.png"
        self.assertTrue(file_range(dest_file, 15118))

    def test_post_fully_populated_sticker_view_accessible(self):
        from stickercode.views import LabelViews

        post_dict = {"submit":"submit", "serial":"UT5555",
                     "domain":"https://waspho.com"}
        request = testing.DummyRequest(post_dict)
        inst = LabelViews(request)
        result = inst.qr_label()
       
        request = testing.DummyRequest()
        request.matchdict["serial"] = "UT5555"
        inst = LabelViews(request)
        result = inst.show_label()

        file_size = result.content_length
        self.assertTrue(size_range(file_size, 15118))

    def test_unknown_sticker_serial_view_is_failure(self):
        from stickercode.views import LabelViews

        request = testing.DummyRequest()
        request.matchdict["serial"] = "badSerial1"
        inst = LabelViews(request)
        self.assertRaises(OSError, inst.show_label)

    def test_post_with_invalid_background_size_uses_default(self):
        from stickercode.views import LabelViews
        
    
        png_name = "resources/wrong_size_wasatch.png"
        png_file = DeformMockFieldStorage(png_name)
        png_upload_dict = {"upload":png_file}
 
        post_dict = {"submit":"submit", "serial":"UT5555",
                     "domain":"https://waspho.com",
                     "upload":png_upload_dict}

        request = testing.DummyRequest(post_dict)
        inst = LabelViews(request)
        result = inst.qr_label()

        dest_file = "label_files/ut5555/label.png"
        self.assertTrue(file_range(dest_file, 15118))

        
class FunctionalTests(unittest.TestCase):
    def setUp(self):
        self.clean_test_files()
        from stickercode import main
        settings = {}
        app = main({}, **settings)
        self.testapp = TestApp(app)

    def tearDown(self):
        del self.testapp

    def clean_test_files(self):
        # Remove the directory if it exists
        test_serials = ["ft789"]

        for item in test_serials:
            dir_out = "thumbnails/%s" % slugify(item)
            if os.path.exists(dir_out):
                shutil.rmtree(dir_out)

    def test_home_form_starts_empty_placeholders_visible(self):
        res = self.testapp.get("/")
        self.assertEqual(res.status_code, 200)

        form = res.forms["deform"]
        self.assertEqual(form["serial"].value, "")

        indexed_form_name = form.get("upload", 0).name
        self.assertEqual(indexed_form_name, "upload")

        match_example = "assets/img/example_qr_label.png"
        self.assertTrue(match_example in res.body)

    def test_imagery_placeholder_is_accessible(self):
        res = self.testapp.get("/assets/img/example_qr_label.png")
        self.assertEqual(res.status_code, 200)

    def test_submit_with_no_values_has_error_messages(self):
        res = self.testapp.get("/")
        form = res.forms["deform"]
        submit_res = form.submit("submit")
        self.assertTrue("was a problem with your" in submit_res.body) 

    def test_submit_with_serial_but_no_domain_has_error_message(self):
        res = self.testapp.get("/")
        form = res.forms["deform"]
        form["serial"] = "okserial"
        form["domain"] = ""
        submit_res = form.submit("submit")
        self.assertTrue("was a problem with your" in submit_res.body) 

    def test_submit_with_all_values_has_no_error_messages(self):
        res = self.testapp.get("/")
        form = res.forms["deform"]
        form["serial"] = "ft789"
        form["domain"] = "https://functional.com"
        form.set("upload", Upload("resources/wasatch.png"), 0)
        submit_res = form.submit("submit")
        self.assertTrue("was a problem with" not in submit_res.body)

    def test_submit_with_all_values_image_links_available(self):
        res = self.testapp.get("/")
        form = res.forms["deform"]
        form["serial"] = "ft789"
        form["domain"] = "https://functional.com"
        form.set("upload", Upload("resources/wasatch.png"), 0)
        submit_res = form.submit("submit")
        self.assertTrue("was a problem with" not in submit_res.body)

        top_link = "src=\"/show_label/ft789"
        self.assertTrue(top_link in submit_res.body)
 
        res = self.testapp.get("/show_label/ft789")
        img_size = res.content_length
        self.assertTrue(size_range(img_size, 15695, ok_range=5000))
