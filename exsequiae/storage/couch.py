from exsequiae.storage import Storage, JSONStorage, DocNode, NodeNotFoundError, Resource, ResourceNotFoundError

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

    def _get_attachment(self, node_name, att_name):
        node = self[node_name]
        if '_attachments' in node.tree:
            atts = node.tree['_attachments']
            if att_name in atts:
                att = atts[att_name]
                return Resource(att_name, self._db.get_attachment(node_name, att_name).read(),
                                att['length'], att['content_type'])
        raise ResourceNotFoundError(att_name)

    def _add_attachment(self, node_name, att_name, data, mime=None):
        self.cache.delete(node_name)
        self._db.put_attachment(self._get(node_name), data, att_name, mime)
        return Resource(att_name, data,
                        len(data), mime)


    def _iter_attachments(self, node_name):
        node = self[node_name]
        if '_attachments' in node.tree:
            for fname in node.tree['_attachments']:
                yield node.get_attachment(fname)
