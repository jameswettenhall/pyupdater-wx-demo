"""
Test updating PyUpdater config.

We don't want this test to be dependent on having a
client_config.py (created by pyupdater init), so
we set the WXUPDATEDEMO_TESTING environment variable
before loading the wxupdatedemo.config module.
"""

import os
import unittest


class PyUpdaterConfigUpdateTester(unittest.TestCase):
    """
    Test ability to update PyUpdater client config
    """
    def setUp(self):
        os.environ['WXUPDATEDEMO_TESTING'] = 'True'

    def test_pyupdater_config_update(self):
        """
        Test ability to update PyUpdater client config
        """
        port = 12345
        from wxupdatedemo.config import CLIENT_CONFIG
        from wxupdatedemo.config import UpdatePyUpdaterClientConfig
        UpdatePyUpdaterClientConfig(clientConfig=None, port=port)
        self.assertEqual(CLIENT_CONFIG.UPDATE_URLS,
                         ['http://127.0.0.1:%s' % port])

    def tearDown(self):
        del os.environ['WXUPDATEDEMO_TESTING']
