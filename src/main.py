"""
Main app entrypoint. Defines routing
"""

import webapp2

import constants
import views.auth
import views.main
import views.webhook

app = webapp2.WSGIApplication([
    ('/', views.main.Main),
    ('/settings', views.main.Settings),
    ('/exp', views.main.Experiment),
    ('/logout', views.auth.Logout),
    (constants.LOGIN_PATH, views.auth.OauthRedirect),
    ('/oauth/callback', views.auth.OauthCallback),
    (r'\/webhooks\/(.+)', views.webhook.Webhook)
], debug=True)

app.error_handlers[404] = views.main.NotFound