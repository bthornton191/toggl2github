import logging
import unittest
import re
from toggl2github.toggl2github import sync


# @unittest.skip('This should only be run manually since it actually affects a live project')
class Test_SyncNNL(unittest.TestCase):
    def test_sync_nnl(self):
        with self.assertLogs(level='INFO') as lc:
            sync('NNL', 1)
            self.assertTrue(any(o.endswith('hours')for o in lc.output))
