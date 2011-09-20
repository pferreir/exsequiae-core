import unittest
import json
import tempfile
import os

from exsequiae.tests.storage import TestBasicOperationsMixin, TestCachingMixin
from exsequiae.storage.couch import CouchStorage

from couchdb.tests.testutil import TempDatabaseMixin

class TestCouchStorage(TempDatabaseMixin, unittest.TestCase, TestBasicOperationsMixin, TestCachingMixin):

    def load(self, data):
        db_name, self._db = self.temp_db()
        for name, content in data.iteritems():
            self._db[name] = content
        self.storage = CouchStorage(db_name)

if __name__ == '__main__':
    unittest.main()
