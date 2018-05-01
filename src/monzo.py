import requests
import requests_toolbelt.adapters.appengine

from config_model import Config

requests_toolbelt.adapters.appengine.monkeypatch()
