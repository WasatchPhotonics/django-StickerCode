""" create png files suitable for printing on the QL700 label maker
design for wasatch photonics device labeling.
"""

import logging

import PyQRNative

from PIL import Image, ImageDraw, ImageFont

log = logging.getLogger(__name__)

class QL700Label(object):
    """ Generate a Wasatch Photonics themed Brother QL-700 label by
    default. All parameters are optional.
    """
    def __init__(self, filename="ql700_label.png", serial="EXAM0123",
                 domain="https://waspho.com", 
                 base_img="resources/wasatch.png"):
        self.filename = filename
        self.serial = serial
        self.domain = domain
        self.base_img = base_img
        self.link_txt = "%s/%s" % (self.domain, self.serial)

        self.font = "resources/libmonoreg.ttf"

        min_length = 4
        max_length = 34
        link_len = len(self.link_txt)

        log.info("Encode: %s (%s)", self.link_txt, link_len)
        if link_len < min_length or link_len > max_length:
            log.critical("Invalid length")
            raise TypeError

        self.generate_qr_image()
        self.build_png()

    def generate_qr_image(self):
        """ Use pyqrnative to build a qr image, and save to disk.
        """
        pyqr = PyQRNative.QRCode(4, PyQRNative.QRErrorCorrectLevel.H)
        
        pyqr.addData(self.link_txt)
        pyqr.make()
        qr_image = pyqr.makeImage()

        img_file = open("resources/temp_qr.png", "wb")
        qr_image = qr_image.resize((320, 320))
        qr_image.save(img_file, 'PNG')
        img_file.close()

    def build_png(self):
        """ Use the established parameters to create an image using
        pillow suitable for printing at 300x600 on brother ql700.
        """

        # Open the base image, draw text
        back_img = Image.open(self.base_img)

        txt_draw = ImageDraw.Draw(back_img)

        font = ImageFont.truetype(self.font, 30)
        txt_draw.text((140, 205), self.link_txt, font = font)


        # Composite over the generated qr code
        qr_img = Image.open("resources/temp_qr.png")
        back_img.paste(qr_img, (730, 0))

        back_img.save(self.filename)

        
    
