"""
Abstract functionality for all view classes to chare
"""
import logging

import webapp2

import constants
from .exceptions import LoginRequiredError


class BaseHandler(webapp2.RequestHandler):
    def handle_exception(self, exception, debug_mode):
        logging.exception(exception)
        if isinstance(exception, LoginRequiredError):
            self.redirect(constants.LOGIN_PATH)
        else:
            super(BaseHandler, self).handle_exception(exception, debug_mode)