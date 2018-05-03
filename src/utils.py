"""
Helper functions
"""
import logging
from gaesessions import get_current_session

from models import User
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

    return user


def get_partner(session=None):
    """
    Gets the user's partner based on the session
    """
    user = get_user(session)
    return User.get(user.partner_id)