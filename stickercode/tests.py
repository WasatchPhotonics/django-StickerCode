""" unit and functional tests for sticker code creation and web service
wrapper.
"""

import os
import sys
import logging
import unittest

from stickercode.coverage_utils import touch_erase

log = logging.getLogger()
log.setLevel(logging.DEBUG)

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
        self.assertEqual(actual_size, 32743)

if __name__ == "__main__":
    unittest.main()
