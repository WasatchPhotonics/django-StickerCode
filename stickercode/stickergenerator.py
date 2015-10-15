""" create png files suitable for printing on the QL700 label maker
design for wasatch photonics device labeling.
"""

from PIL import Image, ImageDraw, ImageFont

class QL700Label(object):
    """ Generate a Wasatch Photonics themed Brother QL-700 label by
    default. All parameters are optional.
    """
    def __init__(self, filename="ql700_label.png", serial="EXAMPLE",
                 domain="https://waspho.com", 
                 base_img="resources/wasatch.png"):
        self.filename = filename
        self.serial = serial
        self.domain = domain
        self.base_img = base_img

        if len(serial) < 4 or len(serial) > 20:
            log.critical("Invalid serial length")
            raise TypeError

        self.generate_qr_image()
        self.build_png()

    def generate_qr_image(self):
        """ Use pyqrnative to build a qr image, and save to disk.
        """
        return
        qr = PyQRNative.QRCode(4, PyQRNative.QRErrorCorrectLevel.H)
        qr.addData(in_url)
        qr.make()
        im = qr.makeImage()

        img_file = open('imagery\qr_resize.png', 'wb')
        im = im.resize((300,300))
        im.save(img_file, 'PNG')
        img_file.close()

    def build_png(self):
        """ Use the established parameters to create an image using
        pillow suitable for printing at 300x600 on brother ql700.
        """

        
        # Open the base image, draw text
        link_txt = "%s/%s" % (self.domain, self.serial)
        back_img = Image.open(self.base_img)



        txt_draw = ImageDraw.Draw(back_img)

        font = ImageFont.truetype("LiberationMono-Regular.ttf", 30)
        txt_draw.text((140, 205), link_txt, font = font)

        back_img.save(self.filename)

        
    
