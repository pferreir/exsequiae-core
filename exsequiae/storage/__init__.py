"""
Storage module

Future improvements could include some sort of MVCC
"""

import datetime
from werkzeug.contrib.cache import SimpleCache

cache = SimpleCache()


class CacheWrapper(object):

    def __init__(self, storage, cache):
        self._storage = storage
        self._cache = cache

    def get(self, key):
        return cache.get("%s_%s" % (self._storage.unique_id, key))

    def set(self, key, value):
        return cache.set("%s_%s" % (self._storage.unique_id, key), value)

    def delete(self, key):
        return cache.delete("%s_%s" % (self._storage.unique_id, key))


class CacheException(Exception):
    pass


class Storage(object):

    _registered = {}

    def __init__(self):
        self.cache = CacheWrapper(self, cache)

    @classmethod
    def replicate(cls, other_storage, **params):
        new_storage = cls(initialize=True, **params)
        for name, doc in other_storage:
            new_doc = new_storage.new(name)
            new_doc.metadata = doc.metadata
            new_doc.data = doc.data
            new_doc.save()

    @staticmethod
    def register(ident):
        def _wrapper(sclass):
            Storage._registered[ident] = sclass
            return sclass
        return _wrapper

    @classmethod
    def initialize(cls, config):
        stype, sparams = config.get('STORAGE_TYPE'), config.get('STORAGE_PARAMS')
        if stype not in cls._registered:
            raise Exception("Storage type '%s' not available" % stype)
        else:
            return cls._registered[stype](**sparams)

    def new(self, name):
        node = self._node_class(self, name)
        return node

    def load(self, name, fail_on_miss=False, bypass_cache=False):
        node = self.new(name)

        if bypass_cache:
            tree = self._load_not_cached(node)
        else:
            entry = self.cache.get(name)
            if entry != None:
                tree = entry
            else:
                # cache miss
                if fail_on_miss:
                    raise CacheException('MISS')
                tree = self._load_not_cached(node)
                self.cache.set(name, tree)

        tree = self._unserialize(tree)

        node.metadata = tree['metadata']
        node.data = tree['data']
        node.tree = tree
        return node

    def save(self, node, before_commit=lambda: 0):
        obj = node.tree
        obj.update(self._serialize({'metadata': node.metadata, 'data': node.data}))
        self.cache.delete(node._name)
        self._save(node, obj, before_commit=before_commit)

        return obj

    def __getitem__(self, key):
        return self.load(key)

    def get(self, key, fail_on_miss=False, bypass_cache=False):
        return self.load(key, fail_on_miss=fail_on_miss, bypass_cache=bypass_cache)

class DocNode(object):

    def __init__(self, storage, name):
        self._storage = storage
        self._name = name
        self._loaded = False
        self.tree = {}
        super(DocNode, self).__init__()

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, metadata):
        self._metadata = metadata

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    def save(self, before_commit=lambda: 0):
        self._storage.save(self, before_commit=before_commit)


class JSONStorage(Storage):

    def _unserialize(self, entry):
        md = entry['metadata']
        for key, val in md.iteritems():
            if key == 'date':
                md[key] = datetime.datetime.strptime(val, "%Y-%m-%d")
        return entry

    def _serialize(self, entry):
        md = entry['metadata']
        for key, val in md.iteritems():
            if key == 'date':
                md[key] = datetime.datetime.strftime(val, "%Y-%m-%d")
        return entry


from exsequiae.storage import file, couch
