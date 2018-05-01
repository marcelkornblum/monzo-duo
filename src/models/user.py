from google.appengine.ext import ndb
from google.appengine.ext.ndb import model


class User(ndb.Model):
    """Models an individual user"""
    refresh_token = ndb.StringProperty()
    partner_id = ndb.StringProperty()
    account_id = ndb.StringProperty()

    @classmethod
    def get(cls, user_id):
        entity = cls(key=model.Key(cls, user_id))

        def txn(): return None if not entity.key.get() else entity.key
        return model.transaction(txn).get()

    @classmethod
    def get_or_create(cls, user_id):
        entity = cls(key=model.Key(cls, user_id))

        def txn(): return entity.put() if not entity.key.get() else entity.key
        return model.transaction(txn).get()
