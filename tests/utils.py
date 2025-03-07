import operator
import unittest

from nose.plugins.skip import SkipTest

from mongoengine import connect
from mongoengine.connection import get_db, disconnect_all
from mongoengine.mongodb_support import get_mongodb_version


MONGO_TEST_DB = 'mongoenginetest'   # standard name for the test database


class MongoDBTestCase(unittest.TestCase):
    """Base class for tests that need a mongodb connection
    It ensures that the db is clean at the beginning and dropped at the end automatically
    """

    @classmethod
    def setUpClass(cls):
        disconnect_all()
        cls._connection = connect(db=MONGO_TEST_DB)
        cls._connection.drop_database(MONGO_TEST_DB)
        cls.db = get_db()

    @classmethod
    def tearDownClass(cls):
        cls._connection.drop_database(MONGO_TEST_DB)
        disconnect_all()


def get_as_pymongo(doc):
    """Fetch the pymongo version of a certain Document"""
    return doc.__class__.objects.as_pymongo().get(id=doc.id)


def _decorated_with_ver_requirement(func, mongo_version_req, oper):
    """Return a MongoDB version requirement decorator.

    The resulting decorator will raise a SkipTest exception if the current
    MongoDB version doesn't match the provided version/operator.

    For example, if you define a decorator like so:

        def requires_mongodb_gte_36(func):
            return _decorated_with_ver_requirement(
                func, (3.6), oper=operator.ge
            )

    Then tests decorated with @requires_mongodb_gte_36 will be skipped if
    ran against MongoDB < v3.6.

    :param mongo_version_req: The mongodb version requirement (tuple(int, int))
    :param oper: The operator to apply (e.g: operator.ge)
    """
    def _inner(*args, **kwargs):
        mongodb_v = get_mongodb_version()
        if oper(mongodb_v, mongo_version_req):
            return func(*args, **kwargs)

        raise SkipTest('Needs MongoDB v{}+'.format('.'.join(str(n) for n in mongo_version_req)))

    _inner.__name__ = func.__name__
    _inner.__doc__ = func.__doc__
    return _inner
