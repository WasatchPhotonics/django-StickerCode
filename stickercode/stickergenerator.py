""" create png files suitable for printing on the QL700 label maker
design for wasatch photonics device labeling.
"""

import os
import logging

import PyQRNative

from PIL import Image, ImageDraw, ImageFont

log = logging.getLogger(__name__)

class QL700Label(object):
    """ Generate a Wasatch Photonics themed Brother QL-700 label by
    default. All parameters are optional.
    """
    def __init__(self, filename="ql700_label.png", serial="EX-0158",
                 domain="http://waspho.com", 
                 base_img="resources/wasatch.png",
                 return_blob=False):
        self.filename = filename
        self.serial = serial
        self.domain = domain
        self.dir_name = os.path.dirname(__file__)
        self.base_img = "%s/../%s" % (self.dir_name, base_img)
        self.link_txt = "%s/%s" % (self.domain, self.serial)

        self.font_sans = "%s/../resources/libsansreg.ttf" \
                         % self.dir_name
        self.font_reg = "%s/../resources/libmonoreg.ttf" \
                         % self.dir_name
        self.font_bold = "%s/../resources/libmonobold.ttf" \
                         % self.dir_name

        min_length = 4
        max_length = 33
        link_len = len(self.link_txt)

        log.info("Encode: %s (%s)", self.link_txt, link_len)
        if link_len < min_length or link_len > max_length:
            log.critical("Invalid length")
            raise TypeError

        self.generate_qr_image()
        self.build_png()
        if not return_blob:
            self.save_png()
        
    def return_blob(self):
        """ API compatibility to return generated blob data from qr
        label without writing to disk. If you have a solution with
        tobytes, bytesio and encoder_name, please let me know.
        """
        self.back_img.save("temp_file.png")
        self.back_img.close()
        temp_file = open("temp_file.png")
        return temp_file.read()

    def generate_qr_image(self):
        """ Use pyqrnative to build a qr image, and save to disk.
        """
        pyqr = PyQRNative.QRCode(4, PyQRNative.QRErrorCorrectLevel.H)
        
        pyqr.addData(self.link_txt)
        pyqr.make()
        qr_image = pyqr.makeImage()

        # Resize the image so it first nicely on the graphic
        img_file = open("%s/../resources/temp_qr.png" \
                        % self.dir_name, "wb")
        qr_image = qr_image.resize((320, 320))
        qr_image.save(img_file, 'PNG')
        img_file.close()

    def build_png(self):
        """ Use the established parameters to create an image using
        pillow suitable for printing at 300x600 on brother ql700.
        """

        # Open the base image, draw text
        self.back_img = Image.open(self.base_img)
        txt_draw = ImageDraw.Draw(self.back_img)
        font = ImageFont.truetype(self.font_sans, 30)

        dtxt = "%s/" % self.domain
        txt_draw.text((145, 205), dtxt, font=font)

        bold_font = ImageFont.truetype(self.font_bold, 40)
        txt_draw.text((395, 198), self.serial, font=bold_font)

        # Composite over the generated qr code
        qr_img = Image.open("%s/../resources/temp_qr.png" \
                            % self.dir_name)
        self.back_img.paste(qr_img, (730, 0))


    def save_png(self):
        """ Write the in-memory png to disk.
        """
        self.back_img.save(self.filename)
        
