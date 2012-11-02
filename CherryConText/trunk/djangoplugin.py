# -*- coding: utf-8 -*-
import imp
import os, os.path

import cherrypy
from cherrypy.process import plugins

from django.conf import settings
from django.core.handlers.wsgi import WSGIHandler

from httplogger import HTTPLogger

__all__ = ['DjangoAppPlugin']

class DjangoAppPlugin(plugins.SimplePlugin):
    def __init__(self, bus, settings_module='settings', wsgi_http_logger=HTTPLogger):
        """ CherryPy engine plugin to configure and mount
        the Django application onto the CherryPy server.
        """
        plugins.SimplePlugin.__init__(self, bus)
        os.environ['DJANGO_SETTINGS_MODULE'] = settings_module
        self.wsgi_http_logger = wsgi_http_logger

    def start(self):
        """ When the bus starts, the plugin is also started
        and we load the Django application. We then mount it on
        the CherryPy engine for serving as a WSGI application.
        We let CherryPy serve the application's static files.
        """
        cherrypy.log("Loading and serving the Django application")
        cherrypy.tree.graft(self.wsgi_http_logger(WSGIHandler()))
        settings = self.load_settings()
        static_handler = cherrypy.tools.staticdir.handler(
            section="/",
            dir=os.path.split(settings.STATIC_ROOT)[1],
            root=os.path.abspath(os.path.split(settings.STATIC_ROOT)[0])
        )
        cherrypy.tree.mount(static_handler, settings.STATIC_URL)

    def load_settings(self):
        """ Loads the Django application's settings. You can
        override this method to provide your own loading
        mechanism. Simply return an instance of your settings module.
        """
        name = os.environ['DJANGO_SETTINGS_MODULE']
        package, mod = name.rsplit('.', 1)
        fd, path, description = imp.find_module(mod, [package.replace('.', '/')])

        try:
            return imp.load_module(mod, fd, path, description)
        finally:
            if fd: fd.close()
