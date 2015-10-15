""" pyramid web views for stickercode label creation.
"""

class StickerForm(object):
    serial = "changetonull"

class LabelViews(object):
    """ Return forms and png objects for post generated content.
    """
    def __init__(self, request):
        self.request = request

    def qr_label(self):
        """ Process form parameters, create a qr code or return an empty
        form.
        """
        if "form.submitted" not in self.request.params:
            return dict(fields=self.empty_form())

    def empty_form(self):
        """ Populate an empty form object, return to web app.
        """
        return StickerForm()
        
