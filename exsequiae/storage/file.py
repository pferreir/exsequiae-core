import os, json, datetime, threading
from exsequiae.storage import Storage, JSONStorage, DocNode


class FileDocNode(DocNode):
    def __init__(self, storage, name):
        super(FileDocNode, self).__init__(storage, name)
        self._fpath = os.path.join(self._storage.path, "%s.json" % name)



@Storage.register('file')
class DirStorage(JSONStorage):
    _node_class = FileDocNode

    def __init__(self, path):
        self._path = path
        self._index = {}
        self._build_index()
        self.unique_id = self._path.replace('/', '_')
        self._w_lock = threading.Lock()
        super(DirStorage, self).__init__()

    def _load_not_cached(self, node):
        # acquire and release immediately, just making sure any ongoing operations
        # finish first
        with self._w_lock:
            pass
        with open(node._fpath, 'r') as f:
            tree = json.load(f)

        return tree

    def _build_index(self):
        for fname in os.listdir(self._path):
            fpath = os.path.join(self._path, fname)
            if os.path.isfile(fpath):
                base, ext = os.path.splitext(fname)
                if ext == ".json":
                    self._index[base] = FileDocNode(self, fname)

    @property
    def path(self):
        return self._path

    def __iter__(self):
        for key, node in self._index.iteritems():
            yield key, self.load(key)

    def __contains__(self, key):
        return key in self._index

    def _save(self, node, obj, before_commit=lambda: 0):
        self._w_lock.acquire()
        with open(node._fpath, 'w') as f:
            json.dump(obj, f)
            before_commit()
            f.flush()
            os.fsync(f.fileno())
        self._index[node._name] = obj
        self._w_lock.release()
