"""
Top level view code
"""

import jinja2

from constants import TRANSACTION_CATEGORIES
# from models import User
import utils
from .base import BaseHandler

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader('templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class Main(BaseHandler):
    """Home page"""

    def get(self):
        """ Render home page"""
        user = utils.get_user()
        partner = utils.get_partner()
        user_balance = user.get_balance()
        partner_balance = partner.get_balance()
        message = "Your balance is GBP %i and your partner's is GBP %i" % (
            user_balance['balance'], partner_balance['balance'])

        template_values = {
            'text': message,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


class Settings(BaseHandler):
    """Deals with all the user settings"""

    def get(self):
        """Render settings page"""
        user = utils.get_user()
        template = JINJA_ENVIRONMENT.get_template('settings.html')

        user = utils.get_user()

        template_values = {
            'text': "Make changes and hit save",
            'accounts': user.list_accounts(),
            'user': user,
            'transaction_categories': TRANSACTION_CATEGORIES
        }
        self.response.write(template.render(template_values))

    def post(self):
        """ Handle form submission """
        user = utils.get_user()

        user.display_name = self.request.get('display_name', user.display_name)
        user.display_initials = self.request.get(
            'display_initials', user.display_initials)
        user.account_id = self.request.get('account_id', user.account_id)
        user.notify_categories = self.request.get_all(
            'notify_categories', [])
        user.notify_daily = bool(self.request.get(
            'notify_daily', user.notify_daily))
        user.notify_weekly = bool(self.request.get(
            'notify_weekly', user.notify_weekly))
        user.notify_monthly = bool(self.request.get(
            'notify_monthly', user.notify_monthly))
        user.notify_spend_over = self.request.get(
            'notify_spend_over', user.notify_spend_over)
        user.put()

        user = utils.get_user()

        template = JINJA_ENVIRONMENT.get_template('settings.html')
        template_values = {
            'text': "Make changes and hit save",
            'accounts': user.list_accounts(),
            'user': user,
            'transaction_categories': TRANSACTION_CATEGORIES
        }
        self.response.write(template.render(template_values))


class NotFound(BaseHandler):
    """Not Found page"""

    def get(self):
        """ Render 404 page"""
        template = JINJA_ENVIRONMENT.get_template('404.html')
        self.error(404)
        self.response.write(template.render())


class Experiment(BaseHandler):
    """Just a place to test stuff out"""

    def get(self):
        """ render experiemntal page"""
        # user = utils.get_user()

        user = utils.get_user()
        user.add_webhook()
        webhooks = user.list_webhooks()

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write(webhooks[0])
