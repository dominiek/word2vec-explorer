
import sys
import os
import cherrypy
from cherrypy.lib.static import serve_file
from explorer import Model

STATIC_DIR = os.path.dirname(os.path.realpath(__file__)) + '/public'
CACHE = {}

class App(object):
    @cherrypy.expose
    def index(self):
        return serve_file(STATIC_DIR + '/index.html', "text/html")


class Explore(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self, query=None, limit=1000):
        req = cherrypy.request
        limit = int(limit)
        cache_key = query + '-' + str(limit)
        result = CACHE.get(cache_key, {})
        if len(result) > 0:
            return {'result': CACHE[cache_key], 'cached': True}
        exploration = self.model.explore(query, limit=limit)
        exploration.reduce()
        exploration.cluster()
        result = exploration.serialize()
        CACHE[cache_key] = result
        return {'result': result, 'cached': False}


if __name__ == '__main__':
    #cherrypy.config.update({'/': {'tools.staticdir.on': True, 'tools.staticdir.dir': STATIC_DIR}})
    app = App()
    app.model = Model(sys.argv[1])
    app.explore = Explore()
    app.explore.model = app.model
    cherrypy.quickstart(app, '/', {'/': {'tools.staticdir.on': True, 'tools.staticdir.dir': STATIC_DIR}})
