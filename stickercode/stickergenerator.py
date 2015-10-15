""" create png files suitable for printing on the QL700 label maker
design for wasatch photonics device labeling.
"""

class QL700Label(object):
    """ Generate a Wasatch Photonics themed Brother QL-700 label by
    default. All parameters are optional.
    """
    def __init__(self, filename="ql700_label.png", serial="EXAMPLE",
                       domain="waspho.com", base_img="wasatch.png"):
        self.filename = filename
        self.serial = serial
        self.domain = domain
        self.base_img = base_img

        self.build_png()

    def build_png(self):
        """ Use the established parameters to create an image using
        pillow suitable for printing at 300x600 on brother ql700.
        """
        
    
