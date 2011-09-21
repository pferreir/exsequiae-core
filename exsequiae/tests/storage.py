import threading
import StringIO
from datetime import datetime

from exsequiae.storage import CacheException, NodeNotFoundError, ResourceNotFoundError


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

    def testDelete(self):
        self.load(STORAGE_DATA_SIMPLE)
        del self.storage['doc1']
        self.assertRaises(NodeNotFoundError, self.storage.get, 'doc1')

    def testRetrieveNonExisting(self):
        self.load(STORAGE_DATA_SIMPLE)
        self.assertRaises(NodeNotFoundError, self.storage.get, 'doc3')

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


class TestAttachmentsMixin(object):

    def testAttachmentAdd(self):
        self.load(STORAGE_DATA_SIMPLE)
        doc1 = self.storage.get('doc1')
        doc1.add_attachment('att1', StringIO.StringIO('i shall taunt you one more time'))
        self.assertEqual(doc1.get_attachment('att1', bypass_cache=True).data.read(), 'i shall taunt you one more time')

    def testAttachmentRetrieval(self):
        self.load(STORAGE_DATA_SIMPLE)
        doc2 = self.storage.get('doc2')
        self.assertRaises(ResourceNotFoundError, doc2.get_attachment, 'att1')
        doc2.add_attachment('att1', StringIO.StringIO('i shall taunt you one more time'))
        self.assertEqual(len(doc2.get_attachment('att1').data.read()), 31)

    def testAttachmentIteration(self):
        self.load(STORAGE_DATA_SIMPLE)
        doc2 = self.storage.get('doc2')
        taunts = {
            'att1': 'i shall taunt you one more time',
            'att2': 'i shall taunt yet another time',
            'att3': 'i shall taunt you... yet another time'
            }

        for k, v in taunts.iteritems():
            doc2.add_attachment(k, StringIO.StringIO(v))

        for att in doc2:
            self.assertEqual(att.data.read(), taunts[att.name])

    def testAttachmentCaching(self):
        self.load(STORAGE_DATA_SIMPLE)
        doc1 = self.storage.get('doc1')

        # on add, caching is done
        doc1.add_attachment('att1', StringIO.StringIO('i shall taunt you one more time'))
        self.assertEqual(doc1.get_attachment('att1').data.read(), 'i shall taunt you one more time')
        # now let's clear everything and test caching on read
        self.storage.cache.clear()

        # first load
        self.assertEqual(doc1.get_attachment('att1').data.read(), 'i shall taunt you one more time')
        # now this one can't fail
        self.assertEqual(doc1.get_attachment('att1', fail_on_miss=True).data.read(), 'i shall taunt you one more time')
