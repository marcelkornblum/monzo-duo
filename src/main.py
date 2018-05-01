"""
Main app entrypoint. Defines routing
"""

import webapp2

import views

app = webapp2.WSGIApplication([
    ('/', views.Main),
    ('/exp', views.Experiment),
    ('/logout', views.Logout),
    ('/oauth/redirect', views.OauthRedirect),
    ('/oauth/callback', views.OauthCallback),
], debug=True)
