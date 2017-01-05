"""
Test ability to launch wxupdatedemo GUI
"""
import os
import unittest

from wxupdatedemo.main import PyUpdaterWxDemoApp


class PyUpdaterWxDemoTester(unittest.TestCase):
    """
    Test ability to launch wxupdatedemo GUI
    """
    def __init__(self, *args, **kwargs):
        super(PyUpdaterWxDemoTester, self).__init__(*args, **kwargs)
        self.app = None

    def setUp(self):
        os.environ['WXUPDATEDEMO_TESTING'] = 'True'
        fileServerPort = 12345
        status = "No updates available"
        self.app = PyUpdaterWxDemoApp(fileServerPort, status)

    def test_wxupdatedemo(self):
        """
        Test ability to launch wxupdatedemo GUI
        """
        assert self.app.frame.IsShown()

    def tearDown(self):
        """
        Destroy the app
        """
        if self.app:
            self.app.frame.Hide()
            self.app.frame.Destroy()
        del os.environ['WXUPDATEDEMO_TESTING']
