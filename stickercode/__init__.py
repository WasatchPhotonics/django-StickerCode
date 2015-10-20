""" Defines application main, routes and configuration options for the
pyramid application.
"""
from pyramid.config import Configurator

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application. Check the
    config/.ini files for more information.
    """
    config = Configurator(settings=settings)
    config.include("pyramid_chameleon")
    config.add_static_view("assets", "assets", cache_max_age=3600)
    config.add_route("qr_label", "/")
    config.add_route("show_label", "/show_label/{serial}")
    config.add_route("blank_label", "/show_label/")
    config.scan()
    return config.make_wsgi_app()
