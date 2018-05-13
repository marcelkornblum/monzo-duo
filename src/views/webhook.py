#coding=utf8
"""
Processing for webhooks
"""
import json
import logging
import webapp2

from models.user import User


class Webhook(webapp2.RequestHandler):
    """Home page"""

    def get(self, webhook_code):
        """ GET not supported"""
        self.response.status = 405
        self.response.write("Method Not Allowed")

    def post(self, webhook_code):
        """Webhook listener for transaction info sent from Monzo"""
        body = json.loads(self.request.body)
        if body['type'] == 'transaction.created':
            data = body['data']

            query = User.query(User.webhook_code == webhook_code)
            users = query.fetch(1)
            for user in users: # got to be a neater way to do this - i only want ONE!
                # get partner's immediate notification prefs
                # partner = User.get(user.partner_id)
                # compare categories, amounts
                # perhaps add feed item

                # for now just notify the user
                amount = 0 - data['amount']

                title = "%s at %s" % (amount, data['description'])
                logging.info("posting feed item: %s)", title)
                user.create_feed_item(title)
