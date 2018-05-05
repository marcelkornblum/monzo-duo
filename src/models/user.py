# pylint: disable=E0401
import os
from base64 import b64encode
import calendar
from datetime import datetime, timedelta
from google.appengine.ext import ndb
from google.appengine.ext.ndb import model
import logging

import monzo


class User(ndb.Model):
    """Models an individual user"""
    refresh_token = ndb.StringProperty()
    access_token = ndb.StringProperty()
    partner_id = ndb.StringProperty()
    account_id = ndb.StringProperty()
    display_name = ndb.StringProperty()
    display_initials = ndb.StringProperty()
    webhook_code = ndb.StringProperty()
    notify_categories = ndb.JsonProperty()
    notify_daily = ndb.BooleanProperty()
    notify_weekly = ndb.BooleanProperty()
    notify_monthly = ndb.BooleanProperty()
    notify_spend_over = ndb.IntegerProperty()
    field_defaults = {
        'display_name': 'NOT SET',
        'notify_categories': [],
        'notify_daily': False,
        'notify_weekly': False,
        'notify_monthly': True,
        'notify_spend_over': 1000,
    }

    @classmethod
    def get(cls, user_id):
        entity = cls(key=model.Key(cls, user_id))

        def txn():
            return None if not entity.key.get() else entity.key
        return model.transaction(txn).get()

    @classmethod
    def get_or_create(cls, user_id):
        entity = cls(key=model.Key(cls, user_id))

        def txn():
            return entity.put() if not entity.key.get() else entity.key
        return model.transaction(txn).get()

    def get_field(self, field_name):
        """
        Retrieval method that ensures e.g. unset fields have useful shape
        """
        default_value = self.field_defaults.get(field_name, None)
        value = getattr(self, field_name, default_value)
        if value is None and default_value is not None:
            value = default_value
        return value

    def is_setup(self):
        """
        Returns a boolean indicating whether the user is fully set up
        """
        if (self.refresh_token is not None and
            self.access_token is not None and
            self.account_id is not None and
            self.partner_id is not None and
                self.webhook_code is not None):
            return True

        return False

    #
    # API methods
    #
    def list_accounts(self):
        """
        Gets a list of the user's non-closed accounts
        """
        return monzo.list_accounts(self)

    def get_balance(self):
        """
        Gets the balance of the user's set account
        """
        return monzo.get_balance(self)

    def list_webhooks(self):
        """
        Returns a list of the user's webhooks
        """
        return monzo.list_webhooks(self)

    def add_webhook(self):
        """
        Adds a new webhook for the user, using a unique code saved to the user object
        """
        if self.webhook_code is None:
            self.webhook_code = b64encode(os.urandom(8)).decode('utf-8')
            self.put()

        # only allow one webhook for this app per user
        for webhook in self.list_webhooks():
            if self.webhook_code in webhook['url']:
                logging.info(
                    "add_webhook found existing webhook, aborting [%s]", webhook)
                return None

        return monzo.add_webhook(self)

    def delete_webhook(self, webhook_id=None):
        """
        Deletes the given webhook, or the webhook with the code stored on the user object
        """
        if webhook_id is None:
            for webhook in self.list_webhooks():
                if self.webhook_code in webhook['url']:
                    webhook_id = webhook.id
        return monzo.delete_webhook(self, webhook_id)

    def list_transactions(self, limit=None, since=None, before=None):
        """
        Gets a list of the user's transactions
        """
        return monzo.list_transactions(self, limit, since, before)

    def list_recent_transactions(self, limit=100, days=7):
        """
        Returns a filtered list of the user's most recent outgoing transactions
        """
        before = datetime.now()
        since = datetime.now().replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        ) - timedelta(days=days)
        transactions = monzo.list_transactions(self,
                                               limit=limit,
                                               since=since.strftime(
                                                   '%Y-%m-%dT%H:%M:%SZ'),
                                               before=before.strftime(
                                                   '%Y-%m-%dT%H:%M:%SZ')
                                               )
        return [x for x in transactions if (x['amount'] < 0 and x['scheme'] != 'uk_retail_pot') and 'decline_reason' not in x]

    def list_recent_category_expenses(self):
        """
        Gives a dict of category: subtotal of (<100) (outgoing) transactions this month
        """
        today = datetime.now()
        # all days of month so far
        days = (today.day - 1)
        # + calendar.monthrange(today.year, today.month)[1]) # all last month's days
        transactions = self.list_recent_transactions(limit=100, days=days)
        categories = {}
        for trx in transactions:
            if trx['category'] not in categories:
                categories[trx['category']] = {
                    'total': 0,
                    'count': 0
                }
            categories[trx['category']]['total'] += trx['amount']
            categories[trx['category']]['count'] += 1
        return categories

    def get_transaction(self, transaction_id):
        """
        Gets a single transaction
        """
        return monzo.get_transaction(self, transaction_id)

    def annotate_transaction(self, transaction_id, payload):
        """
        Add key=value pairs to a specific transaction
        """
        return monzo.annotate_transaction(self, transaction_id, payload)

    def create_user_feed_item(self, title, image_url, **kwargs):
        """
        Creates a feed item on the user's feed
        """
        return monzo.create_feed_item(self, title, image_url, **kwargs)
