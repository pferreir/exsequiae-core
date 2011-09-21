import unittest
import json
import tempfile
import os

from exsequiae.tests.storage import TestBasicOperationsMixin, TestCachingMixin, TestAttachmentsMixin
from exsequiae.storage.file import DirStorage


class TestDirStorage(unittest.TestCase, TestBasicOperationsMixin, TestCachingMixin,
                     TestAttachmentsMixin):

    def load(self, data):
        fs_dir = tempfile.mkdtemp()
        for name, content in data.iteritems():
            with open(os.path.join(fs_dir, "%s.json" % name), 'w') as f:
                json.dump(content, f)
        
        self.storage = DirStorage(fs_dir)

if __name__ == '__main__':
    unittest.main()
