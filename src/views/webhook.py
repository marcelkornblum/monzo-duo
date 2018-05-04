"""
Processing for webhooks
"""
import logging
import webapp2

from models.user import User


class Webhook(webapp2.RequestHandler):
    """Home page"""

    def get(self, webhook_code):
        """ GET not supported"""
        # self.response.status = 405
        # self.response.write("Method Not Allowed")
        query = User.query(User.webhook_code == webhook_code)
        users = query.fetch(1)
        for user in users:
            self.response.write(user.account_id)

    def post(self, webhook_code):
        """Webhook listener for transaction info sent from Monzo"""
        logging.info("webhook received: %s",
                     self.request.get('data', 'NO_DATA'))
