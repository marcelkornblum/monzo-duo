import jinja2
import webapp2

from gaesessions import get_current_session
from models import User
from monzo import refresh_access_token, get_accounts

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader('templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class Main(webapp2.RequestHandler):
    """Home page"""

    def get(self):
        session = get_current_session()
        token = session.get('access_token', None)
        if token is None:
            self.redirect('/oauth/redirect')

        user = User.get(session['monzo_id'])
        message = 'retrieved from Data Store'
        accounts = []

        if user.account_id is None:
            accounts = get_accounts()
            user.account_id = accounts[0]['id']
            user.put()
            message = 'retrieved from API'

        template_values = {
            'text': message,
            'accounts': accounts,
            'account_id': user.account_id
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


class Experiment(webapp2.RequestHandler):
    """Just a place to test stuff out"""

    def get(self):
        session = get_current_session()
        user = User.get(session['monzo_id'])
        old_session_token = session['access_token']
        old_refresh_token = user.refresh_token
        (status, response) = refresh_access_token(old_refresh_token)

        if status == 200:
            session['access_token'] = response['access_token']
            user.refresh_token = response['refresh_token']
            user.put()
            message = 'REFRESHED'
        else:
            message = '[ERROR %i] %s' % (status, response)
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write("%s\r\n\r\nSESSIONS:\r\n\r\nold token: %s \r\n\r\nnew token: %s\r\n\r\nREFRESHES:\r\n\r\nold: %s\r\n\r\nnew: %s" %
                            (message, old_session_token, session['access_token'], old_refresh_token, user.refresh_token))
