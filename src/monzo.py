"""
Wrappers for Monzo API calls, including some logic
"""
# pylint: disable=E1101,E0401
import logging
from google.appengine.api import urlfetch

import requests
import requests_toolbelt.adapters.appengine

from constants import URL_BASE, MONZO_CLIENT_ID, MONZO_CLIENT_SECRET

requests_toolbelt.adapters.appengine.monkeypatch()
urlfetch.set_default_fetch_deadline(45)


REDIRECT_URI = '%s/oauth/callback' % URL_BASE
WEBHOOK_URI = '%s/webhooks' % URL_BASE
API_BASE = 'https://api.monzo.com'


def build_oauth_redirect(state):
    """
    Creates the oAuth redirect target
    """
    client_id = MONZO_CLIENT_ID
    redirect_uri = REDIRECT_URI
    redirect_tgt = ('https://auth.monzo.com/?client_id=%s'
                    '&redirect_uri=%s&response_type=code&state=%s') % (
                        client_id, redirect_uri, state)

    return redirect_tgt.encode('utf8')


def _call_api(endpoint, payload=None, auth_token=None, method='GET'):
    """
    Basic wrapper for API calls to handle repetitive code
    """
    uri = '%s%s' % (API_BASE, endpoint)

    if auth_token is not None:
        headers = {'Authorization': 'Bearer %s' % auth_token}
    else:
        headers = None

    try:
        if method == 'GET':
            api_call = requests.get(uri, params=payload, headers=headers)
        elif method == 'POST':
            api_call = requests.post(uri, payload, headers=headers)
        elif method == 'PUT':
            api_call = requests.put(uri, payload, headers=headers)
        elif method == 'PATCH':
            api_call = requests.patch(uri, payload, headers=headers)
        elif method == 'DELETE':
            api_call = requests.delete(uri, headers=headers)

        logging.info("[%s] %s", method, api_call.url)
    except urlfetch.errors.DeadlineExceededError:
        return _call_api(endpoint, payload=payload, auth_token=auth_token, method=method)

    if api_call.status_code != requests.codes.ok:
        logging.error(
            "Error communicating with the Monzo API [%i]: %s", api_call.status_code, api_call.text)
        response = "Something went wrong with the token exchange."
    else:
        response = api_call.json()

        # VERY DANGEROUS LOGGING CALL!!
        # logging.info("DATA from API call to '%s': %s", endpoint, response)

    return (api_call.status_code, response)


def exchange_oauth_token(auth_code):
    """
    Swaps the returned oAuth code for an Auth token for use on following calls
    """
    payload = {
        'grant_type': 'authorization_code',
        'client_id': MONZO_CLIENT_ID,
        'client_secret': MONZO_CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'code': auth_code
    }

    return _call_api('/oauth2/token', payload, None, 'POST')


def refresh_access_token(refresh_token):
    """
    Uses the refresh token to retrieve a new auth token
    """
    payload = {
        'grant_type': 'refresh_token',
        'client_id': MONZO_CLIENT_ID,
        'client_secret': MONZO_CLIENT_SECRET,
        'refresh_token': refresh_token
    }

    return _call_api('/oauth2/token', payload, None, 'POST')


def _call_user_api(user, url, payload=None, **kwargs):
    """
    Adds token refresh functionality and user identity switching to basic API call handler
    """
    updated_kwargs = dict(kwargs, auth_token=user.access_token)
    if payload is not None:
        updated_kwargs['payload'] = payload

    (status, response) = _call_api(url, **updated_kwargs)

    if status == 401:
        (refresh_status, refresh_response) = refresh_access_token(
            user.refresh_token)
        logging.info('refresh access token status: %i', refresh_status)

        if refresh_status == requests.codes.ok:
            user.access_token = refresh_response['access_token']
            user.refresh_token = refresh_response['refresh_token']
            user.put()

            updated_kwargs['auth_token'] = user.access_token

            return _call_api(url, **updated_kwargs)

        return (refresh_status, refresh_response)

    return (status, response)


def list_accounts(user):
    """
    Gets a list of the user's non-closed accounts
    """
    (status, data) = _call_user_api(user, '/accounts')
    if status != requests.codes.ok:
        return []

    return [x for x in data['accounts'] if x['closed'] is False]


def get_balance(user):
    """
    Gets the balance of the user's set account
    """
    (status, data) = _call_user_api(user, '/balance', {
        'account_id': user.account_id
    })
    if status != requests.codes.ok:
        return {}
    return data


def list_webhooks(user):
    """
    Returns a list of the user's webhooks
    """
    (status, data) = _call_user_api(user, '/webhooks', {
        'account_id': user.account_id
    })
    if status != requests.codes.ok:
        return []
    return data['webhooks']


def add_webhook(user):
    """
    Adds a new webhook for the user, using a unique code saved to the user object
    """
    if user.webhook_code is None:
        return (400, "User has no webhook_code attribute")

    (status, data) = _call_user_api(user, '/webhooks', {
        'account_id': user.account_id,
        'url': '%s/%s' % (WEBHOOK_URI, user.webhook_code)
    }, method='POST')
    if status != requests.codes.ok:
        return None
    return data['webhook']


def delete_webhook(user, webhook_id):
    """
    Deletes the given webhook
    """
    return _call_user_api(user, '/webhooks/%s' % webhook_id, method='DELETE')


def list_transactions(user, limit=None, since=None, before=None):
    """
    Gets a list of the user's transactions
    """
    (status, data) = _call_user_api(user, '/transactions?expand[]=merchant', {
        'account_id': user.account_id,
        'limit': limit,
        'before': before,
        'since': since,
    })
    if status != requests.codes.ok:
        return []
    return data['transactions']


def get_transaction(user, transaction_id):
    """
    Gets a single transaction
    """
    (status, data) = _call_user_api(user, '/transactions/%s' % transaction_id)
    if status != requests.codes.ok:
        return None
    return data['transaction']


def annotate_transaction(user, transaction_id, payload):
    """
    Add key=value pairs to a specific transaction
    """
    metadata = [dict({"metadata[%s]" % k: v})
                for i in payload for k, v in i.items()]
    (status, data) = _call_user_api(user, '/transactions/%s' %
                                    transaction_id, metadata, method='PATCH')
    if status != requests.codes.ok:
        return None
    return data['transaction']


def create_feed_item(user, title, image_url, **kwargs):
    """
    Adds an item to the given user's app feed
    """
    params = {
        'account_id': user.account_id,
        'type': 'basic',
        'params[title]': title,
        'params[image_url]': image_url,
    }
    for key, val in kwargs.iteritems():
        if key == 'url':
            params[key] = val
        else:
            params['params[%s]' % key] = val

    return _call_user_api(user, '/feed', params, method='POST')
