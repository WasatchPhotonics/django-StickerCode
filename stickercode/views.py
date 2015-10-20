""" pyramid web views for stickercode label creation.
"""

import os
import shutil
import logging

import colander

from PIL import Image

from slugify import slugify
 
from deform import Form, widget, FileData
from deform.exception import ValidationFailure

from pyramid.view import view_config
from pyramid.response import FileResponse

from stickercode.stickergenerator import QL700Label

log = logging.getLogger(__name__)

class MemoryTmpStore(dict):
    """ Instances of this class implement the
    :class:`deform.interfaces.FileUploadTempStore` interface
    This is ripped from the deform2demo code: 
    https://github.com/Pylons/deformdemo/blob/master/deformdemo/\
        __init__.py
    If you attempt to make tmpstore a class of FileUploadTempStore as
    described in the stack overflow entry below, it complains about
    the missing implementation of preview_url.
    """
    def preview_url(self, uid):
        """ provide interface for schemanode
        """
        return None


class StickerSchema(colander.Schema):
    """ use colander to define a data validation schema for linkage with
    a deform object.
    """
    serial = colander.SchemaNode(colander.String(),
                                 validator=colander.Length(3, 10),
                                 description="Max 10 character serial")

    domain = colander.SchemaNode(colander.String(),
                                 validator=colander.url,
                                 default="https://waspho.com",
                                 description="Valid URL")

    # Based on: # http://stackoverflow.com/questions/6563546/\
    # how-to-make-file-upload-facultative-with-deform-and-colander
    # Various demos delete this temporary file on succesful submission
    tmpstore = MemoryTmpStore()
    fuw = widget.FileUploadWidget(tmpstore)
    upload = colander.SchemaNode(FileData(), 
                                 missing=colander.null,
                                 widget=fuw,
                                 description="Background Image")


class StickerForm(object):
    """ placeholder class for generating empty sticker form data.
    """
    serial = ""
    domain = "https://waspho.com"
    slugged = ""
    filename = ""
    upload = ""

class LabelViews(object):
    """ Return forms and png objects for post generated content.
    """
    def __init__(self, request):
        self.request = request

    @view_config(route_name="blank_label")
    def blank_label(self):
        """ Match a route without the serial in matchdict, return the
        placeholder image.
        """
        log.info("Return blank label")
        return FileResponse("resources/example_qr_label.png")

    @view_config(route_name="show_label")
    def show_label(self):
        """ Return the specified file based on the matchdict serial
        parameter, or the placeholder image if not found.
        """
        serial = self.request.matchdict["serial"]
        filename = "label_files/%s/label.png" % slugify(serial)

        if not os.path.exists(filename):
            filename = "resources/example_qr_label.png"

        return FileResponse(filename)

    @view_config(route_name="qr_label", renderer="templates/qr_form.pt")
    def qr_label(self):
        """ Process form parameters, create a qr code or return an empty
        form.
        """

        schema = StickerSchema()
        form = Form(schema, buttons=("submit",))
        local = self.empty_form()    

        if "submit" in self.request.POST:
            log.info("in form submitted %s", self.request.POST)
            try:
                # Deserialize into hash on validation - capture is the
                # appstruct in deform land
                controls = self.request.POST.items()
                captured = form.validate(controls)

                # Populate local data structure with deserialized data
                local.serial = captured["serial"]
                local.domain = captured["domain"]
                local.slugged = slugify(local.serial)

                # file not required
                if captured["upload"] == colander.null:
                    local.filename = "using default"
                else:
                    local.filename = captured["upload"]["filename"]
                    local.upload = captured["upload"]
                    self.write_file(local)
                    self.check_file_size(local)

                # build the qr label
                self.build_qr_label(local) 

                # Re-render the form with the fields already populated 
                return dict(data=local, form=form.render(captured))
                
            except ValidationFailure as exc:
                #log.exception(exc)
                log.critical("Validation failure, return default form")
                return dict(data=local, form=exc.render())

        return dict(data=local, form=form.render())

    def build_qr_label(self, local):
        """ Create the label_files sub directory on disk if required, then
        generate the qr label and save it in the directory.
        """
        serial = slugify(local.serial)
        dir_name = "label_files/%s" % serial
        filename = "label_files/%s/label.png" % serial
        if os.path.exists(dir_name):
            log.info("Path exists: %s", dir_name)
        else:
            os.makedirs(dir_name)

        # Render with the custom uploaded background if it exists
        back_name = "%s/custom_background.png" % dir_name
        if os.path.exists(back_name):
            lbl = QL700Label(filename=filename, serial=local.serial,
                             domain=local.domain, base_img=back_name)
        else:
            lbl = QL700Label(filename=filename, serial=local.serial,
                             domain=local.domain)
        log.info("Label generated [%s]", lbl)

    def check_file_size(self, upload_obj):
        """ If a custom_background image for that serial number exists
        on disk, delete it if it is the wrong size.
        """
        final_dir = "label_files/%s" % slugify(upload_obj.serial)
        img_file = "%s/custom_background.png" % final_dir
        if os.path.exists(img_file): 
            img = Image.open(img_file)
            (width, height) = img.size
            if width != 1050 or height != 329:
                log.critical("Wrong file size: %s, %s", width, height)
                os.remove(img_file)


    def write_file(self, upload_obj):
        """ With file from the post request, write to a temporary file,
        then ultimately to the destination specified.
        """
        temp_file = "label_files/temp_file"

        upload_file = upload_obj.upload["fp"]
        upload_file.seek(0)
        with open(temp_file, "wb") as output_file:
            shutil.copyfileobj(upload_file, output_file)

        # Create the directory if it does not exist
        final_dir = "label_files/%s" % slugify(upload_obj.serial)
        if not os.path.exists(final_dir):
            log.info("Make directory: %s", final_dir)
            os.makedirs(final_dir)

        final_file = "%s/custom_background.png" % final_dir

        os.rename(temp_file, final_file)
        log.info("Saved file: %s", final_file)

    def empty_form(self):
        """ Populate an empty form object, return to web app.
        """
        return StickerForm()
