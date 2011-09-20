from exsequiae.storage import Storage, JSONStorage, DocNode

try:
    __import__('couchdb')
except ImportError:
    raise Exception("Please install python-couchdb")

from couchdb.client import Server, DEFAULT_BASE_URL
from couchdb.mapping import DateTimeField


class CouchNode(DocNode):

    def _load_not_cached(self):
        tree = self._storage._get(self._name)
        return tree


@Storage.register('couch')
class CouchStorage(JSONStorage):

    _node_class = CouchNode

    def __init__(self, db, url=DEFAULT_BASE_URL, initialize=False):
        self._url = url
        self._server = Server(url)
        self.unique_id = "%s_%s" % (self._url, db)
        super(CouchStorage, self).__init__()

        if db not in self._server:
            if initialize:
                self._server.create(db)
            else:
                raise Exception("DB '%s' not found at %s" % (db, url))
        self._db = self._server[db]

    def __iter__(self):
        for row in self._db.view('_all_docs'):
            yield row.id, row

    def __contains__(self, key):
        return key in self._db

    def __setitem__(self, key, value):
        self._db[key] = value

    def _get(self, key):
        return self._db[key]

    def _save(self, node, obj, before_close=lambda: 0):
        self[node._name] = obj
        before_close()
