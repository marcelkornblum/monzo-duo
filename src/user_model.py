from google.appengine.ext import ndb
from google.appengine.ext.ndb import model


class User(ndb.Model):
    """Models an individual user"""
    refresh_token = ndb.StringProperty()
    partner_id = ndb.StringProperty()

    @classmethod
    def get(cls, user_id):
        entity = cls(key=model.Key(cls, user_id))

        def txn(): return False if not entity.key.get() else entity.key
        retval = model.transaction(txn).get()

    @classmethod
    def create_or_update(cls, user_id, refresh_token):
        entity = cls(key=model.Key(cls, user_id))
        entity.populate(refresh_token=refresh_token)

        def txn(): return entity.put() if not entity.key.get() else entity.key
        retval = model.transaction(txn).get()
        return retval
