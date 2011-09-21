import os, json, datetime, threading, base64, shutil
from exsequiae.storage import Storage, JSONStorage, DocNode, NodeNotFoundError, ResourceNotFoundError, Resource


class FileDocNode(DocNode):
    def __init__(self, storage, name):
        super(FileDocNode, self).__init__(storage, name)
        self._fpath = os.path.join(self._storage.path, "%s.json" % name)



@Storage.register('file')
class DirStorage(JSONStorage):
    _node_class = FileDocNode

    def __init__(self, path, **kwargs):
        self._path = path
        self._index = {}
        self._build_index()
        self.unique_id = self._path.replace('/', '_')
        self._w_lock = threading.Lock()
        super(DirStorage, self).__init__(**kwargs)

    def _load_not_cached(self, node):
        # acquire and release immediately, just making sure any ongoing operations
        # finish first
        if node._name not in self._index:
            raise NodeNotFoundError()
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
                    self._index[base] = FileDocNode(self, base)

    @property
    def path(self):
        return self._path

    def __iter__(self):
        for key, node in self._index.iteritems():
            yield key, self.load(key)

    def __contains__(self, key):
        return key in self._index

    def _delete(self, key):
        os.remove(self._index[key]._fpath)
        att_path = "%s_resources" % self._index[key]._fpath
        if os.path.exists(att_path):
            shutil.rmtree(att_path)
        del self._index[key]

    def _save(self, node, obj, before_commit=lambda: 0):
        self._w_lock.acquire()
        with open(node._fpath, 'w') as f:
            json.dump(obj, f)
            before_commit()
            f.flush()
            os.fsync(f.fileno())
        self._index[node._name] = node
        self._w_lock.release()

    def _get_attachment(self, node_name, att_name):
        node = self[node_name]
        res_path = "%s_resources" % node._fpath
        att_path = os.path.join(res_path, att_name)

        if not os.path.exists(att_path):
            raise ResourceNotFoundError(att_name)
        else:
            with open(att_path, 'r') as f:
                tree = json.load(f)

        return Resource(att_name, base64.decodestring(tree['content']), **tree['metadata'])

    def _add_attachment(self, node_name, att_name, content, mime=None):
        node = self[node_name]
        res_path = "%s_resources" % node._fpath
        if not os.path.exists(res_path):
            os.mkdir(res_path)
        tree = {'metadata':{ 'length': len(content),
                             'mime': mime },
                'content': base64.encodestring(content)}
        with open(os.path.join(res_path, att_name), 'w') as f:
            json.dump(tree, f)
        return Resource(att_name, content, **tree['metadata'])

    def _iter_attachments(self, node_name):
        node = self[node_name]
        res_path = "%s_resources" % node._fpath
        if os.path.exists(res_path):
            for fname in os.listdir(res_path):
                rpath = os.path.join(res_path, fname)
                if os.path.isfile(rpath):
                    yield node.get_attachment(fname)
