""" pyramid web views for stickercode label creation.
"""

import logging
import colander
        
from deform import Form
from deform.exception import ValidationFailure

from pyramid.view import view_config

log = logging.getLogger(__name__)

class StickerSchema(colander.Schema):
    """ use colander to define a data validation schema for linkage with
    a deform object.
    """
    serial = colander.SchemaNode(colander.String(),
                description="Non empty serial")


class StickerForm(object):
    serial = ""

class LabelViews(object):
    """ Return forms and png objects for post generated content.
    """
    def __init__(self, request):
        self.request = request

    @view_config(route_name="qr_label", renderer="templates/home.pt")
    def qr_label(self):
        """ Process form parameters, create a qr code or return an empty
        form.
        """

        schema = StickerSchema()
        form = Form(schema, buttons=("submit",))
        local_data = self.empty_form()    

        log.info("in form submitted %s", self.request.POST)
        if "submit" in self.request.POST:
            try:
                # Deserialize into hash on validation - capture is the
                # appstruct in deform land
                controls = self.request.POST.items()
                captured = form.validate(controls)

                # Populate local data structure with deserialized data
                local_data.serial = captured["serial"]
              
                # Re-render the form with the fields already populated 
                return dict(data=local_data, form=form.render(captured))
                
            except ValidationFailure as e:
                log.exception(e)
                log.critical("Validation failure, return empty form")

        return dict(data=local_data, form=form.render())

    def empty_form(self):
        """ Populate an empty form object, return to web app.
        """
        return StickerForm()

    #@view_config(route_name="deform_view", renderer="templates/home.pt")
    #def deform_view(self):
        #schema = Schema()
        #myform = Form(schema, buttons=('submit',))

        #appstruct = self.empty_form()
        #appstruct.serial = "deformnull"

        #schema = StickerSchema()
        #form = Form(schema, buttons=('submit',))
        #return dict(form=form, appstruct=appstruct)
