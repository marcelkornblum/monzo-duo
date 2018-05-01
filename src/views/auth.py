"""
Auth-related views
"""
import os
from base64 import b64encode
import logging

import jinja2
import webapp2

from gaesessions import get_current_session
from models.user import User
import monzo


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader('templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class Logout(webapp2.RequestHandler):
    """Destroys user session data"""

    def get(self):
        session = get_current_session()
        if session.get('access_token', None) is not None:
            del session['access_token']
        if session.get('monzo_id', None) is not None:
            del session['monzo_id']

        self.response.write(
            JINJA_ENVIRONMENT.get_template("logout.html").render())


class OauthRedirect(webapp2.RequestHandler):
    """Builds the initial app oAuth redirect URI"""

    def get(self):
        session = get_current_session()
        state = session.get('state', None)
        if state is None:
            state = b64encode(os.urandom(16)).decode('utf-8')
            session['state'] = state

        redirect_url = monzo.build_oauth_redirect(state)
        logging.info('redirecting user to %s', redirect_url)

        self.redirect(redirect_url)
        # this should never be seen - but I think it's best practice to end the
        # call with a write() ?
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('redirecting')


class OauthCallback(webapp2.RequestHandler):
    """Handles the oAuth callback, builds session and datastore info"""

    def get(self):
        status_code = 200

        session = get_current_session()
        session_state = session.get('state', None)
        returned_state = self.request.GET['state']
        if session_state is None:
            status_code = 400
            response_text = "State cookie not set or expired. Maybe you took too long to authorize. Please try again."
            logging.info("No state param found on session")
        elif returned_state is None:
            status_code = 400
            response_text = "State not set on response. Please try again."
            logging.info("No state param found on oAuth response")
        elif session_state != returned_state:
            status_code = 400
            response_text = "State validation failed"
            logging.info("State params not equal")
        else:
            auth_code = self.request.GET['code']

            (status_code, responses) = monzo.exchange_oauth_token(auth_code)

            if status_code != 200:
                response_text = responses
                logging.info("Error from oAuth exchange method")
            else:
                # Successful token exchange; set up session and Datastore
                logging.info("Successful oAuth token exchange")
                session.regenerate_id()
                session['access_token'] = responses['access_token']
                session['monzo_id'] = responses['user_id']

                user = User.get_or_create(responses['user_id'])
                user.refresh_token = responses['refresh_token']
                user.put()

        if status_code != 200:
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.status = status_code
            self.response.write(response_text)
        else:
            self.redirect('/')
