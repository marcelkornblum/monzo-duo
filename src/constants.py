import os

from models.config import Config

TRANSACTION_CATEGORIES = (
    'general',
    'eating_out',
    'expenses',
    'transport',
    'cash',
    'bills',
    'entertainment',
    'shopping',
    'holidays',
    'groceries'
)

LOGIN_PATH = '/oauth/redirect'
ENV = 'production'
URL_BASE = 'https://monzo-duo-202412.appspot.com'
APP_LOGO = 'https://pbs.twimg.com/profile_images/2226984247/spoon_400x400.jpg'
MONZO_CLIENT_ID = Config.get('MONZO_CLIENT_ID')
MONZO_CLIENT_SECRET = Config.get('MONZO_CLIENT_SECRET')

if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/') is False:
    ENV = 'local'
    URL_BASE = 'http://localhost:8080'
    MONZO_CLIENT_ID = os.getenv('CONFIG_MONZO_CLIENT_ID')
    MONZO_CLIENT_SECRET = os.getenv('CONFIG_MONZO_CLIENT_SECRET')
