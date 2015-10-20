""" pyramid web views for stickercode label creation.
"""

import os
import logging

import colander

from slugify import slugify
 
from deform import Form
from deform.exception import ValidationFailure

from pyramid.view import view_config
from pyramid.response import FileResponse

from stickercode.stickergenerator import QL700Label

log = logging.getLogger(__name__)

class StickerSchema(colander.Schema):
    """ use colander to define a data validation schema for linkage with
    a deform object.
    """
    serial = colander.SchemaNode(colander.String(),
                validator=colander.Length(3, 10),
                description="Maximum 10 character serial")
    domain = colander.SchemaNode(colander.String(),
                validator=colander.url,
                default="https://waspho.com",
                description="Valid URL")

class StickerForm(object):
    serial = ""
    domain = "https://waspho.com"

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
        filename = "database/%s/label.png" % slugify(serial)

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
        local.slugged = slugify(local.serial)

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
 
                # build the qr label
                self.build_qr_label(local) 
                # Re-render the form with the fields already populated 
                return dict(data=local, form=form.render(captured))
                
            except ValidationFailure as e:
                log.exception(e)
                log.critical("Validation failure, return form")
                return dict(data=local, form=e.render())

        return dict(data=local, form=form.render())

    def build_qr_label(self, local):
        """ Create the database sub directory on disk if required, then
        generate the qr label and save it in the directory.
        """
        serial = slugify(local.serial)
        dir_name = "database/%s" % serial
        filename = "database/%s/label.png" % serial
        if os.path.exists(dir_name):
            log.info("Path exists: %s", dir_name)
        else:
            os.makedirs(dir_name)

        lbl = QL700Label(filename=filename, serial=local.serial,
                         domain=local.domain)

    def empty_form(self):
        """ Populate an empty form object, return to web app.
        """
        return StickerForm()
