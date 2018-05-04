"""
Helper functions
"""
import logging
from dateutil.parser import parse
from gaesessions import get_current_session

from models.user import User
import views.exceptions


def get_user(session=None):
    """
    Gets the user object based on the session, redirects if not available
    """
    if session is None:
        session = get_current_session()
    user_id = session.get('monzo_id', None)

    if user_id is None:
        raise views.exceptions.LoginRequiredError()

    user = User.get(user_id)
    if not user.is_setup():
        raise views.exceptions.UserSetupRequiredError()

    return user


def get_partner(session=None):
    """
    Gets the user's partner based on the session
    """
    user = get_user(session)
    if user.partner_id is None:
        return None

    return User.get(user.partner_id)


def date_format(date_str):
    """
    Gets a string represneting a date, formats it nicely and returns a new string
    """
    return parse(date_str).strftime('%A %-d %B')
