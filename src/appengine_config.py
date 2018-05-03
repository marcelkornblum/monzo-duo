from google.appengine.ext import vendor

# Add any libraries install in the "lib" folder.
vendor.add('lib')

from gaesessions import SessionMiddleware


def webapp_add_wsgi_middleware(app):
    app = SessionMiddleware(
        app, cookie_key="ygKPXOOvBPDehOv7ZTYinuWKXlykeftZ4pPUIQzwMdeX1Qa61TF7kLlG5J3a")
    return app
