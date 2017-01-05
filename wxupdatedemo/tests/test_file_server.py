"""
Test ability to run file server
"""
import threading
import tempfile
import unittest
import os

import requests

from wxupdatedemo.fileserver import RunFileServer
from wxupdatedemo.fileserver import WaitForFileServerToStart
from wxupdatedemo.fileserver import ShutDownFileServer
from wxupdatedemo.fileserver import LOCALHOST
from wxupdatedemo.utils import GetEphemeralPort


class FileServerTester(unittest.TestCase):
    """
    Test ability to run file server
    """
    def __init__(self, *args, **kwargs):
        super(FileServerTester, self).__init__(*args, **kwargs)
        self.fileServerThread = None
        self.fileServerPort = None
        self.testFileName = "testfile.txt"
        self.testFileContent = "Hello, world!"

    def setUp(self):
        tempFile = tempfile.NamedTemporaryFile()
        self.fileServerDir = tempFile.name
        tempFile.close()
        os.mkdir(self.fileServerDir)
        testFilePath = os.path.join(self.fileServerDir, self.testFileName)
        with open(testFilePath, 'w') as testFile:
            testFile.write(self.testFileContent)
        os.environ['PYUPDATER_FILESERVER_DIR'] = self.fileServerDir
        os.environ['WXUPDATEDEMO_TESTING'] = 'True'

    def test_file_server(self):
        """
        Test ability to run file server
        """
        self.fileServerPort = GetEphemeralPort()
        self.fileServerThread = \
            threading.Thread(target=RunFileServer,
                             args=(self.fileServerDir, self.fileServerPort))
        self.fileServerThread.start()
        WaitForFileServerToStart(self.fileServerPort)
        url = "http://%s:%s" % (LOCALHOST, self.fileServerPort)
        url = "%s/%s" % (url, self.testFileName)
        response = requests.get(url, timeout=1)
        self.assertEqual(response.text, self.testFileContent)

    def tearDown(self):
        """
        Shut down file server
        """
        ShutDownFileServer(self.fileServerPort)
        self.fileServerThread.join()
        del os.environ['PYUPDATER_FILESERVER_DIR']
        del os.environ['WXUPDATEDEMO_TESTING']
