""" pyramid web views for stickercode label creation.
"""

import os
import shutil
import logging

import colander

from PIL import Image

from slugify import slugify
 
from deform import Form
from deform.exception import ValidationFailure

from pyramid.view import view_config
from pyramid.response import FileResponse

from stickercode.models import StickerSchema

from stickercode.stickergenerator import QL700Label

log = logging.getLogger(__name__)

class LabelViews(object):
    """ Return forms and png objects for post generated content.
    """
    def __init__(self, request):
        self.request = request

    @view_config(route_name="show_label")
    def show_label(self):
        """ Return the specified file based on the matchdict serial
        parameter, or the placeholder image if not found.
        """
        serial = slugify(self.request.matchdict["serial"])
        filename = "label_files/%s/label.png" % serial
        return FileResponse(filename)

    @view_config(route_name="qr_label", renderer="templates/qr_form.pt")
    def qr_label(self):
        """ Process form parameters, create a qr code or return an empty
        form.
        """
        form = Form(StickerSchema(), buttons=("submit",))

        if "submit" in self.request.POST:
            log.info("submit: %s", self.request.POST)
            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
                rendered_form = form.render(appstruct)

                self.write_optional_uploads(appstruct)
                self.check_background_size(appstruct)
                self.build_qr_label(appstruct) 

                return {"form":rendered_form, "appstruct":appstruct}

            except ValidationFailure as exc: 
                #log.exception(exc)
                log.info("Validation failure")
                return {'form':exc.render()} 

        return {"form":form.render()}

    def build_qr_label(self, appstruct):
        """ Create the label_files sub directory on disk if required, then
        generate the qr label and save it in the directory.
        """
        serial = slugify(appstruct["serial"])
        dir_name = "label_files/%s" % serial
        if os.path.exists(dir_name):
            log.info("Path exists: %s", dir_name)
        else:
            os.makedirs(dir_name)

        # Render with the custom uploaded background if it exists
        back_name = "%s/custom_background.png" % dir_name
        filename = "label_files/%s/label.png" % serial
        if os.path.exists(back_name):
            lbl = QL700Label(filename=filename,
                             serial=appstruct["serial"],
                             domain=appstruct["domain"], 
                             base_img=back_name)
        else:
            lbl = QL700Label(filename=filename,
                             serial=appstruct["serial"],
                             domain=appstruct["domain"])
                
        log.info("Label generated [%s]", lbl)

    def check_background_size(self, appstruct):
        """ If a custom_background image for that serial number exists
        on disk, delete it if it is the wrong size.
        """
        final_dir = "label_files/%s" % slugify(appstruct["serial"])
        img_file = "%s/custom_background.png" % final_dir
        if os.path.exists(img_file): 
            img = Image.open(img_file)
            (width, height) = img.size
            if width != 1050 or height != 329:
                log.critical("Wrong file size: %s, %s", width, height)
                os.remove(img_file)

    def write_optional_uploads(self, appstruct):
        """ With parameters in the post request, create a destination
        directory then write the uploaded file to a hardcoded filename.
        """

        if appstruct.get("upload") is colander.null:
            log.info("No file submitted for background")
            return
 
        final_dir = "label_files/%s" % slugify(appstruct["serial"])
        if not os.path.exists(final_dir):
            log.info("Make directory: %s", final_dir)
            os.makedirs(final_dir)

        final_file = "%s/custom_background.png" % final_dir
        file_pointer = appstruct["upload"]["fp"]
        self.single_file_write(file_pointer, final_file)

    def single_file_write(self, file_pointer, filename):
        """ Read from the file pointer, write intermediate file, and
        then copy to final destination.
        """
        temp_file = "resources/temp_file"

        file_pointer.seek(0)
        with open(temp_file, "wb") as output_file:
            shutil.copyfileobj(file_pointer, output_file)

        os.rename(temp_file, filename)
        log.info("Saved file: %s", filename) 
