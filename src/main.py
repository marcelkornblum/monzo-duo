"""
Main app entrypoint. Defines routing
"""
import os

import webapp2

import constants
import views.auth
import views.main
import views.webhook

if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/') is False:
    # non-production (local) env
    from dotenv import load_dotenv
    load_dotenv()

app = webapp2.WSGIApplication([
    ('/', views.main.Recent),
    ('/summary', views.main.Summary),
    ('/settings', views.main.Settings),
    ('/exp', views.main.Experiment),
    ('/logout', views.auth.Logout),
    (constants.LOGIN_PATH, views.auth.OauthRedirect),
    ('/oauth/callback', views.auth.OauthCallback),
    (r'\/webhooks\/(.+)', views.webhook.Webhook)
], debug=True)

app.error_handlers[404] = views.main.NotFound
