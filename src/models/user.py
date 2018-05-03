# pylint: disable=E0401
import os
from base64 import b64encode
from google.appengine.ext import ndb
from google.appengine.ext.ndb import model

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

    def list_transactions(self):
        """
        Gets a list of the user's transactions
        """
        return monzo.list_transactions(self)

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
