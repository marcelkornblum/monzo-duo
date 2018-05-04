# coding=utf-8
"""
Top level view code
"""

import logging
import jinja2

from constants import TRANSACTION_CATEGORIES
# from models import User
import utils
from .base import BaseHandler


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader('templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True,
)
JINJA_ENVIRONMENT.filters['date_format'] = utils.date_format


def balance_vars(balance_obj):
    if balance_obj['currency'] == 'GBP':
        symbol = '&pound;'
    elif balance_obj['currency'] == 'USD':
        symbol = '&dollar;'
    elif balance_obj['currency'] == 'EUR':
        symbol = '&euro;'

    return symbol, balance_obj['balance'], balance_obj['spend_today']


def categories_vars(user_cats, partner_cats):
    categories = {}
    for cat in TRANSACTION_CATEGORIES:
        user_total = 0
        user_count = 0
        partner_total = 0
        partner_count = 0
        if cat in user_cats:
            user_total = user_cats[cat]['total']
            user_count = user_cats[cat]['count']
        if cat in partner_cats:
            partner_total = partner_cats[cat]['total']
            partner_count = partner_cats[cat]['count']
        categories[cat] = {
            'user': {
                'total': user_total,
                'count': user_count
            },
            'partner': {
                'total': partner_total,
                'count': partner_count
            }
        }
    return categories


class Recent(BaseHandler):
    """Recent Transactions - acts as home page"""

    def get(self):
        """ Render recents page"""
        user = utils.get_user()
        (user_balance_symbol, user_balance,
         user_spend) = balance_vars(user.get_balance())

        partner = utils.get_partner()
        (partner_balance_symbol, partner_balance,
         partner_spend) = balance_vars(partner.get_balance())

        transactions = sorted(
            (user.list_recent_transactions() + partner.list_recent_transactions()),
            key=lambda x: x['created'],
            reverse=True)

        template_values = {
            'user_display_name': user.get_field('display_name'),
            'user_balance_symbol': user_balance_symbol,
            'user_balance': user_balance,
            'user_spend': user_spend,
            'partner_display_name': partner.get_field('display_name'),
            'partner_balance_symbol': partner_balance_symbol,
            'partner_balance': partner_balance,
            'partner_spend': partner_spend,
            'user_account_id': user.account_id,
            'partner_account_id': partner.account_id,
            'transactions': transactions,
        }

        template = JINJA_ENVIRONMENT.get_template('recent.html')
        self.response.write(template.render(template_values))


class Summary(BaseHandler):
    """Summary of this month's transacitons"""

    def get(self):
        """ Render summary page"""
        user = utils.get_user()
        (user_balance_symbol, user_balance,
         user_spend) = balance_vars(user.get_balance())

        partner = utils.get_partner()
        (partner_balance_symbol, partner_balance,
         partner_spend) = balance_vars(partner.get_balance())

        categories = categories_vars(
            user.list_recent_category_expenses(),
            partner.list_recent_category_expenses()
        )

        template_values = {
            'user_display_name': user.get_field('display_name'),
            'user_balance_symbol': user_balance_symbol,
            'user_balance': user_balance,
            'user_spend': user_spend,
            'partner_display_name': partner.get_field('display_name'),
            'partner_balance_symbol': partner_balance_symbol,
            'partner_balance': partner_balance,
            'partner_spend': partner_spend,
            'categories': categories
        }

        template = JINJA_ENVIRONMENT.get_template('summary.html')
        self.response.write(template.render(template_values))


class Settings(BaseHandler):
    """Deals with all the user settings"""

    def parse_user_fields(self, user):
        """Makes sure the fields we can display are safe"""
        return {
            'display_name': user.get_field('display_name'),
            'display_initials': user.get_field('display_initials'),
            'notify_categories': user.get_field('notify_categories'),
            'notify_daily': user.get_field('notify_daily'),
            'notify_weekly': user.get_field('notify_weekly'),
            'notify_monthly': user.get_field('notify_monthly'),
            'notify_spend_over': user.get_field('notify_spend_over'),
        }

    def get(self):
        """Render settings page"""
        user = utils.get_user()
        partner = utils.get_partner()

        template = JINJA_ENVIRONMENT.get_template('settings.html')

        template_values = {
            'text': "Make changes and hit save",
            'accounts': user.list_accounts(),
            'transaction_categories': TRANSACTION_CATEGORIES,
            'user': self.parse_user_fields(user),
            'partner': self.parse_user_fields(partner),
        }
        self.response.write(template.render(template_values))

    def post(self):
        """ Handle form submission """
        user = utils.get_user()
        partner = utils.get_partner()

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
        user.notify_spend_over = int(self.request.get('notify_spend_over', -1))
        user.put()

        user.add_webhook()
        partner.add_webhook()

        template = JINJA_ENVIRONMENT.get_template('settings.html')
        template_values = {
            'text': "Make changes and hit save",
            'accounts': user.list_accounts(),
            'transaction_categories': TRANSACTION_CATEGORIES,
            'user': self.parse_user_fields(user),
            'partner': self.parse_user_fields(partner),
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
