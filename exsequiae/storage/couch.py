from exsequiae.storage import Storage, JSONStorage, DocNode, NodeNotFoundError

try:
    __import__('couchdb')
    COUCHDB_PRESENT = True
except ImportError:
    COUCHDB_PRESENT = False


from couchdb.client import Server, DEFAULT_BASE_URL
from couchdb.mapping import DateTimeField


class CouchNode(DocNode):
    pass


@Storage.register('couch', COUCHDB_PRESENT)
class CouchStorage(JSONStorage):

    _node_class = CouchNode

    def __init__(self, db, url=DEFAULT_BASE_URL, initialize=False, **kwargs):
        self._url = url
        self._server = Server(url)
        self.unique_id = "%s_%s" % (self._url, db)
        super(CouchStorage, self).__init__(**kwargs)

        if db not in self._server:
            if initialize:
                self._server.create(db)
            else:
                raise Exception("DB '%s' not found at %s" % (db, url))
        self._db = self._server[db]

    def __iter__(self):
        for row in self._db.view('_all_docs'):
            node = self.new(row.id)
            yield row.id, self.load(row.id)

    def __contains__(self, key):
        return key in self._db

    def __setitem__(self, key, value):
        self._db[key] = value

    def _delete(self, key):
        del self._db[key]

    def _get(self, key):
        return self._db.get(key, None)

    def _save(self, node, obj, before_commit=lambda: 0):
        self[node._name] = obj
        before_commit()

    def _load_not_cached(self, node):
        tree = self._get(node._name)
        if tree == None:
            raise NodeNotFoundError()
        else:
            return tree
