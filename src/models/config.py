from os import environ
from google.appengine.ext import ndb
from google.appengine.ext.ndb import model
from pydash import snake_case


class Config(ndb.Model):
    value = ndb.StringProperty()
    value_previous = ndb.StringProperty()

    @classmethod
    def __get_fallback_env_var_name__(cls, name):
        """
        Create a scoped/namespaced env var name.  E.g., CONFIG_SOME_SERVICE_API_KEY
        """
        cls_portion = snake_case(cls.__name__).upper()
        name_portion = name.upper()
        return '%s_%s' % (cls_portion, name_portion)

    @classmethod
    def get(cls, name):
        # Unique canary value (`None` may be a valid value for this config
        # item)
        NOT_SET_VALUE = u'!!!__ NOT SET __!!!'

        # Need to ensure uniqueness in a transaction
        entity = cls(key=model.Key(cls, name))
        entity.populate(value=NOT_SET_VALUE)

        def txn(): return entity.put() if not entity.key.get() else entity.key
        retval = model.transaction(txn).get()

        # Fall back to environment vars
        if retval.value == NOT_SET_VALUE:
            fallback_env_var_name = cls.__get_fallback_env_var_name__(name)
            fallback_value = environ.get(fallback_env_var_name)
            if fallback_value is not None:
                retval.value = fallback_value
                retval.put()
                return fallback_value

        if retval.value == NOT_SET_VALUE:
            raise Exception((
                '%s %s not found in the database. A placeholder ' +
                'record has been created. Go to the Developers Console for your app ' +
                'in App Engine, look up the Settings record with name=%s and enter ' +
                'its value in that record\'s value field.  Or if running locally, set' +
                'env var %s') % (cls.__name__, name, name, cls.__get_fallback_env_var_name__(name)))

        return retval.value


class ConfigSubclass(Config):
    pass
