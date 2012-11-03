# -*- coding: utf-8 -*-
__doc__ = """
Module to host a Django application from within a CherryPy server.

Instead of creating a clone to `runserver` like other similar
packages do, we simply setup and host the Django application
using WSGI and CherryPy's capabilities to serve it.

In order to configure the application, we use the `settings.configure(...)`
function provided by Django.

Finally, since the CherryPy WSGI server doesn't offer a log
facility, we add a straightforward WSGI middleware to do so, based
on the CherryPy built-in logger. Obviously any other log middleware
can be used instead.

Note this application admin site uses the following credentials:
admin/admin

Thanks to Damien Tougas for his help on this recipe.

Modified by BEC to allow automatic opening of web browser
"""
import webbrowser
PORT = 8090
if __name__ == '__main__':
    import cherrypy
    cherrypy.config.update({'server.socket_port': PORT, 'checker.on': False})

    from djangoplugin import DjangoAppPlugin
    DjangoAppPlugin(cherrypy.engine, settings_module='pyConTextKit.settings').subscribe()

    #cherrypy.quickstart()
    #cherrypy.quickstart(script_name="/pyConTextKit/accounts/login/?next=/accounts/login")

    cherrypy.engine.start()
    webbrowser.open_new_tab("http://localhost:%s/pyConTextKit/accounts/login/?next=/accounts/login/"%str(PORT))
    cherrypy.engine.block()

