"""
Unit tests
"""

from exsequiae.tests.dir_storage import *

from exsequiae.storage.couch import COUCHDB_PRESENT
if COUCHDB_PRESENT:
    from exsequiae.tests.couch_storage import *
