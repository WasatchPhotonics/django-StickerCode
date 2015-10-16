""" pyramid web views for stickercode label creation.
"""

import colander

from pyramid.view import view_config

class StickerSchema(colander.Schema):
    """ use colander to define a data validation schema for linkage with
    a deform object.
    """
    serial = colander.SchemaNode(colander.String(),
                default="defaultnull",
                description="Non empty serial")

class Person(colander.MappingSchema):
    name = colander.SchemaNode(colander.String())
    age = colander.SchemaNode(colander.Integer(),
                              validator=colander.Range(0, 200))

class People(colander.SequenceSchema):
    person = Person()

class Schema(colander.MappingSchema):
    people = People()


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

    @view_config(route_name="deform_view", renderer="templates/home.pt")
    def deform_view(self):
        from deform import Form
        schema = Schema()
        myform = Form(schema, buttons=('submit',))

        appstruct = self.empty_form()
        appstruct.serial = "deformnull"

        class TestSchema(colander.Schema):
            artist = colander.SchemaNode(
                colander.String(),
                default='Grandaddy',
                description='Song name')
            album = colander.SchemaNode(
                colander.String(),
                default='Just Like the Fambly Cat')
            song = colander.SchemaNode(
                colander.String(),
                description='Song name')

        schema = StickerSchema()
        form = Form(schema, buttons=('submit',))
        return dict(form=form, appstruct=appstruct)
        return dict(form=myform.render(), appstruct=appstruct)
