import os
import requests
import requests_toolbelt.adapters.appengine
from base64 import b64encode
import webapp2
import logging

from gaesessions import get_current_session
from config_model import Config
from user_model import User

requests_toolbelt.adapters.appengine.monkeypatch()

REDIRECT_URI = 'https://monzo-duo-202412.appspot.com/oauth/callback'


class MainPage(webapp2.RequestHandler):
    def get(self):
        session = get_current_session()
        token = session.get('access_token', None)
        if token is None:
            self.redirect('/oauth/redirect')

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')


class LogoutPage(webapp2.RequestHandler):
    def get(self):
        session = get_current_session()
        del session['access_token']

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write("You have been logged out")


# class ExperimentPage(webapp2.RequestHandler):
#     def get(self):
#         session = get_current_session()

#         self.response.headers['Content-Type'] = 'text/plain'
#         self.response.write(session.get())


class OauthRedirect(webapp2.RequestHandler):
    def get(self):
        session = get_current_session()
        state = session.get('state', None)
        if state is None:
            state = b64encode(os.urandom(16)).decode('utf-8')
            session['state'] = state

        client_id = Config.get('MONZO_CLIENT_ID')
        redirect_uri = REDIRECT_URI
        redirect_tgt = 'https://auth.monzo.com/?client_id=%s&redirect_uri=%s&response_type=code&state=%s' % (
            client_id, redirect_uri, state)
        logging.info('redirecting user to %s' % redirect_tgt)

        self.redirect(redirect_tgt.encode('utf8'))
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('redirecting')


class OauthCallback(webapp2.RequestHandler):
    def get(self):
        status_code = 200

        session = get_current_session()
        session_state = session.get('state', None)
        returned_state = self.request.GET['state']
        if session_state is None:
            status_code = 400
            response_text = "State cookie not set or expired. Maybe you took too long to authorize. Please try again."
        elif returned_state is None:
            status_code = 400
            response_text = "State not set on response. Please try again."
        elif session_state != returned_state:
            status_code = 400
            response_text = "State validation failed"
        else:
            auth_code = self.request.GET['code']

            r = requests.post('https://api.monzo.com/oauth2/token',  {
                'grant_type': 'authorization_code',
                'client_id': Config.get('MONZO_CLIENT_ID'),
                'client_secret': Config.get('MONZO_CLIENT_SECRET'),
                'redirect_uri': REDIRECT_URI,
                'code': auth_code})

            if r.status_code != 200:
                status_code = r.status_code
                response_text = "Something went wrong with the token exchange."
            else:
                responses = r.json()

                session.regenerate_id()
                session['access_token'] = responses['access_token']
                session['monzo_id'] = responses['user_id']

                User.create_or_update(
                    responses['user_id'], responses['refresh_token'])

        if status_code != 200:
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.status = status_code
            self.response.write(response_text)
        else:
            self.redirect('/')


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/logout', LogoutPage),
    # ('/exp', ExperimentPage),
    ('/oauth/redirect', OauthRedirect),
    ('/oauth/callback', OauthCallback),
], debug=True)
