import logging

import requests
import requests_toolbelt.adapters.appengine

from gaesessions import get_current_session

from models import Config, User

requests_toolbelt.adapters.appengine.monkeypatch()


REDIRECT_URI = 'https://monzo-duo-202412.appspot.com/oauth/callback'
API_BASE = 'https://api.monzo.com'


def _call_api(endpoint, payload=None, method='GET', include_auth_header=True):
    """
    Basic wrapper for API calls to handle repetitive code
    """
    session = get_current_session()
    token = session.get('access_token', None)
    uri = '%s%s' % (API_BASE, endpoint)

    if include_auth_header is True:
        headers = {'Authorization': 'Bearer %s' % token}
    else:
        headers = None

    if method == 'GET':
        r = requests.get(uri, params=payload, headers=headers)
    elif method == 'POST':
        r = requests.post(uri, payload, headers=headers)

    if r.status_code != 200:
        logging.error(
            "Error communicating with the Monzo API [%i]: %s", r.status_code, r.text)
        response = "Something went wrong with the token exchange."
    else:
        response = r.json()

        # VERY DANGEROUS LOGGING CALL!!
        # logging.info("DATA from API call to '%s': %s", endpoint, response)

    return (r.status_code, response)


def _call_api_auth(*args, **kwargs):
    """
    Adds token refresh functionality to basic API call handler
    """
    (status, response) = _call_api(*args, **kwargs)

    if status == 401 and kwargs['include_auth_header'] != False:
        session = get_current_session()
        user = User.get(session['monzo_id'])
        (refresh_status, refresh_response) = refresh_access_token(user.refresh_token)

        if refresh_status == 200:
            session['access_token'] = refresh_response['access_token']
            user.refresh_token = refresh_response['refresh_token']
            user.put()

            return _call_api(*args, **kwargs)

        return (refresh_status, refresh_response)

    return (status, response)


def build_oauth_redirect(state):
    client_id = Config.get('MONZO_CLIENT_ID')
    redirect_uri = REDIRECT_URI
    redirect_tgt = 'https://auth.monzo.com/?client_id=%s&redirect_uri=%s&response_type=code&state=%s' % (
        client_id, redirect_uri, state)

    return redirect_tgt.encode('utf8')


def exchange_oauth_token(auth_code):
    payload = {
        'grant_type': 'authorization_code',
        'client_id': Config.get('MONZO_CLIENT_ID'),
        'client_secret': Config.get('MONZO_CLIENT_SECRET'),
        'redirect_uri': REDIRECT_URI,
        'code': auth_code
    }

    return _call_api('/oauth2/token', payload, 'POST', False)


def refresh_access_token(token):
    payload = {
        'grant_type': 'refresh_token',
        'client_id': Config.get('MONZO_CLIENT_ID'),
        'client_secret': Config.get('MONZO_CLIENT_SECRET'),
        'refresh_token': token
    }

    return _call_api('/oauth2/token', payload, 'POST')


def get_accounts():
    (status, data) = _call_api_auth('/accounts')
    if status != 200:
        return []
    else:
        return [x for x in data['accounts'] if x['closed'] is False]
