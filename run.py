"""
run.py

PyUpdaterWxDemo can be launched by running "python run.py"
"""
import logging
import os
import sys
import threading
import time
import argparse

from pyupdater.client import Client

import wxupdatedemo
from wxupdatedemo.main import PyUpdaterWxDemoApp
from wxupdatedemo.fileserver import RunFileServer
from wxupdatedemo.fileserver import WaitForFileServerToStart
from wxupdatedemo.fileserver import ShutDownFileServer
from wxupdatedemo.utils import GetEphemeralPort

from wxupdatedemo.config import CLIENT_CONFIG
from wxupdatedemo.config import UpdatePyUpdaterClientConfig

logger = logging.getLogger(__name__)
STDERR_HANDLER = logging.StreamHandler(sys.stderr)
STDERR_HANDLER.setFormatter(logging.Formatter(logging.BASIC_FORMAT))

class UpdateStatus(object):
    """Enumerated data type"""
    # pylint: disable=invalid-name
    # pylint: disable=too-few-public-methods
    UNKNOWN = 0
    NO_AVAILABLE_UPDATES = 1
    UPDATE_DOWNLOAD_FAILED = 2
    EXTRACTING_UPDATE_AND_RESTARTING = 3
    UPDATE_AVAILABLE_BUT_APP_NOT_FROZEN = 4
    COULDNT_CHECK_FOR_UPDATES = 5

UPDATE_STATUS_STR = \
    ['Unknown', 'No available updates were found.',
     'Update download failed.', 'Extracting update and restarting.',
     'Update available but application is not frozen.',
     'Couldn\'t check for updates.']

def ParseArgs(argv):
    """
    Parse command-line args.
    """
    usage = ("%(prog)s [options]\n"
             "\n"
             "You can also run: python setup.py nosetests")
    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument("--debug", help="increase logging verbosity",
                        action="store_true")
    parser.add_argument("--version", action='store_true',
                        help="displays version")
    return parser.parse_args(argv[1:])


def InitializeLogging(debug=False):
    """
    Initialize logging.
    """
    logger.addHandler(STDERR_HANDLER)
    if debug or 'WXUPDATEDEMO_TESTING' in os.environ:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logger.setLevel(level)
    logging.getLogger("wxupdatedemo.fileserver").addHandler(STDERR_HANDLER)
    logging.getLogger("wxupdatedemo.fileserver").setLevel(level)
    logging.getLogger("pyupdater").setLevel(level)
    logging.getLogger("pyupdater").addHandler(STDERR_HANDLER)


def StartFileServer(fileServerDir):
    """
    Start file server.
    """
    if not fileServerDir:
        message = \
            "The PYUPDATER_FILESERVER_DIR environment variable is not set."
        if hasattr(sys, "frozen"):
            logger.error(message)
            return None
        else:
            fileServerDir = os.path.join(os.getcwd(), 'pyu-data', 'deploy')
            message += "\n\tSetting fileServerDir to: %s\n" % fileServerDir
            logger.warning(message)
    fileServerPort = GetEphemeralPort()
    thread = threading.Thread(target=RunFileServer,
                              args=(fileServerDir, fileServerPort))
    thread.start()
    WaitForFileServerToStart(fileServerPort)
    return fileServerPort


def CheckForUpdates(fileServerPort, debug):
    """
    Check for updates.

    Channel options are stable, beta & alpha
    Patches are only created & applied on the stable channel
    """
    assert CLIENT_CONFIG.PUBLIC_KEY is not None
    client = Client(CLIENT_CONFIG, refresh=True)
    appUpdate = client.update_check(CLIENT_CONFIG.APP_NAME,
                                    wxupdatedemo.__version__,
                                    channel='stable')
    if appUpdate:
        if hasattr(sys, "frozen"):
            downloaded = appUpdate.download()
            if downloaded:
                status = UpdateStatus.EXTRACTING_UPDATE_AND_RESTARTING
                if 'WXUPDATEDEMO_TESTING_FROZEN' in os.environ:
                    sys.stderr.write("Exiting with status: %s\n"
                                     % UPDATE_STATUS_STR[status])
                    ShutDownFileServer(fileServerPort)
                    sys.exit(0)
                ShutDownFileServer(fileServerPort)
                if debug:
                    logger.debug('Extracting update and restarting...')
                    time.sleep(10)
                appUpdate.extract_restart()
            else:
                status = UpdateStatus.UPDATE_DOWNLOAD_FAILED
        else:
            status = UpdateStatus.UPDATE_AVAILABLE_BUT_APP_NOT_FROZEN
    else:
        status = UpdateStatus.NO_AVAILABLE_UPDATES
    return status


def DisplayVersionAndExit():
    """
    Display version and exit.

    In some versions of PyInstaller, sys.exit can result in a
    misleading 'Failed to execute script run' message which
    can be ignored: http://tinyurl.com/hddpnft
    """
    sys.stdout.write("%s\n" % wxupdatedemo.__version__)
    sys.exit(0)


def Run(argv, clientConfig=None):
    """
    The main entry point.
    """
    args = ParseArgs(argv)
    if args.version:
        DisplayVersionAndExit()
    InitializeLogging(args.debug)
    fileServerDir = os.environ.get('PYUPDATER_FILESERVER_DIR')
    fileServerPort = StartFileServer(fileServerDir)
    if fileServerPort:
        UpdatePyUpdaterClientConfig(clientConfig, fileServerPort)
        status = CheckForUpdates(fileServerPort, args.debug)
    else:
        status = UpdateStatus.COULDNT_CHECK_FOR_UPDATES
    if 'WXUPDATEDEMO_TESTING_FROZEN' in os.environ:
        sys.stderr.write("Exiting with status: %s\n"
                         % UPDATE_STATUS_STR[status])
        ShutDownFileServer(fileServerPort)
        sys.exit(0)
    mainLoop = (argv[0] != 'RunTester')
    if not 'WXUPDATEDEMO_TESTING_FROZEN' in os.environ:
        return PyUpdaterWxDemoApp.Run(
            fileServerPort, UPDATE_STATUS_STR[status], mainLoop)
    else:
        return None

if __name__ == "__main__":
    Run(sys.argv)
