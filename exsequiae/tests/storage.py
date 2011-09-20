import threading

from exsequiae.storage import CacheException
from datetime import datetime


STORAGE_DATA_SIMPLE = {'doc1': {'data': 'This is document 1', 'metadata': {}},
                       'doc2': {'data': 'This is document 2', 'metadata': {'language': 'en'}}}

STORAGE_DATA_DATE = {'doc1': {'data': 'This is document 1', 'metadata': {'date': '2001-01-01'}}}


class TestBasicOperationsMixin(object):

    def testProperInitialization(self):
        self.load(STORAGE_DATA_SIMPLE)
        for name, node in self.storage:
            self.assertIn(name, STORAGE_DATA_SIMPLE)
            self.assertEqual(node.tree, STORAGE_DATA_SIMPLE[name])

    def testDateUnSerialization(self):
        self.load(STORAGE_DATA_DATE)
        self.assertEqual(self.storage['doc1'].metadata['date'], datetime(2001, 1, 1))

    def testDataRetrieval(self):
        self.load(STORAGE_DATA_SIMPLE)
        self.assertEqual(self.storage['doc1'].data, 'This is document 1')

    def testDataSave(self):
        self.load(STORAGE_DATA_SIMPLE)
        doc1 = self.storage['doc1']
        doc1.data = 'lorem ipsum bla bla'
        doc1.save()
        doc1_copy = self.storage.get('doc1', bypass_cache=True)

    def testConcurrentSaves(self):
        """
        Basically:
        O1: O...........W..C
        O2: ...O..W..C......
        can't happen (O2 should execute after)
        """
        t_cont = {}
        def concurrent_save():
            def _save():
                doc1.data = 'coiso'
                doc1.save()
            t_cont['t'] = threading.Thread(target=_save)
            t_cont['t'].start()
            
        self.load(STORAGE_DATA_SIMPLE)
        doc1 = self.storage['doc1']
        doc1.data = 'lorem ipsum bla bla'
        doc1.save(before_commit=concurrent_save)
        t_cont['t'].join()
        doc1_copy = self.storage.get('doc1', bypass_cache=True)
        self.assertEqual(doc1_copy.data, 'coiso')

    def testReadLocking(self):
        """
        When files are read, make sure that they are not in the middle of a write op
        Basically read operations should wait till write operations finish
        """
        t_cont = {}
        def concurrent_read():
            def _read():
                doc1_copy = self.storage.get('doc1', bypass_cache=True)
                self.assertEqual(doc1_copy.data, 'lorem ipsum bla bla')
            t_cont['t'] = threading.Thread(target=_read)
            t_cont['t'].start()
            
        self.load(STORAGE_DATA_SIMPLE)
        doc1 = self.storage['doc1']
        doc1.data = 'lorem ipsum bla bla'
        doc1.save(before_commit=concurrent_read)
        t_cont['t'].join()

    
class TestCachingMixin(object):
            
    def testCacheHit(self):
        self.load(STORAGE_DATA_SIMPLE)
        # this should place doc1 in the cache
        self.storage.get('doc1')
        self.storage.get('doc1', fail_on_miss=True)

    def testCacheMiss(self):
        self.load(STORAGE_DATA_SIMPLE)
        # this should place doc1 in the cache
        self.storage.get('doc1')
        self.assertRaises(CacheException, self.storage.get, 'doc2', fail_on_miss=True)
        doc2 = self.storage.get('doc2')
        # a miss doesn't compromise the retrieval operation if fail_on_miss is set to its
        # implicit value
        self.assertEqual(doc2.data, 'This is document 2')

    def testCacheDirty(self):
        self.load(STORAGE_DATA_SIMPLE)
        # this should place doc1 in the cache
        doc1 = self.storage.get('doc1')
        doc1.data = 'now this will be dirty'
        doc1.save()
        # immediately after a save, the cache should be dirty
        self.assertRaises(CacheException, self.storage.get, 'doc1', fail_on_miss=True)

    def testCacheConcurrency(self):
        """
        make sure there is no cache hit while a node is being written
        and that the read operation waits that the write operation finishes
        """
        t_cont = {}
        def concurrent_read():
            def _read():
                doc1_copy = self.storage.get('doc1', bypass_cache=False)
                self.assertEqual(doc1_copy.data, 'lorem ipsum bla bla')
            t_cont['t'] = threading.Thread(target=_read)
            t_cont['t'].start()
            
        self.load(STORAGE_DATA_SIMPLE)
        doc1 = self.storage['doc1']
        doc1.data = 'lorem ipsum bla bla'
        doc1.save(before_commit=concurrent_read)
        t_cont['t'].join()
