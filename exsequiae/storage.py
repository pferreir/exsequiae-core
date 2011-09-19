import os, json, datetime

class Storage(object):

    def new(self, name):
        return self._add(name)
    
    def __init__(self):
        pass


class DocNode(object):
    def __init__(self):
        pass


def load_first(f):
    def wrapper(self):
        if not self._loaded:
            self._load()
        return f(self)
    return wrapper


class FileDocNode(DocNode):
    def __init__(self, storage, name):
        self._storage = storage
        self._loaded = False
        self._fpath = os.path.join(self._storage.path, name)
        super(FileDocNode, self).__init__()

    def _enrich_metadata(self, md):
        for key, val in md.iteritems():
            if key == 'date':
                md[key] = datetime.datetime.strptime(val, "%Y-%m-%d")
        return md

    def _load(self):
        with open(self._fpath, 'r') as f:
            tree = json.load(f)
            self._metadata = self._enrich_metadata(tree['metadata'])
            self._data = tree['data']
        self._loaded = True

    @property
    @load_first
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, metadata):
        self._metadata = metadata

    @property
    @load_first
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    def save(self):
        with open(self._fpath, 'w') as f:
            json.dump({'metadata': self._metadata, 'data': self._data}, f)


class DirStorage(Storage):
    _node_class = FileDocNode
    
    def __init__(self, path):
        self._path = path
        self._index = {}
        self._build_index()
        super(DirStorage, self).__init__()

    def _add(self, name):
        node = self._node_class(self, name)
        self._index[name] = node
        return node

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
            yield key, node

    def __getitem__(self, key):
        return self._index[key]

    def __contains__(self, key):
        return key in self._index
