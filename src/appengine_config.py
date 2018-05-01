from google.appengine.ext import vendor

# Add any libraries install in the "lib" folder.
vendor.add('lib')

from gaesessions import SessionMiddleware


def webapp_add_wsgi_middleware(app):
    app = SessionMiddleware(
        app, cookie_key="!?\xfd\xac\x8e\xa0hip\x1c\xb3\xec\xa1\xaf\x91\x92\x08\x9d:6\xdb;\x8e\xb2F\x15F\xf6\xc16?\xe9p\xaa,\xcf,\xe0\xf2G\xc0\xf1\x96H\x81\xc9\x89\xf6E\xdb]3\xa7\x1aXq\xcf\x07\x97\x14\xca\xea\xdd\xa1")
    return app
