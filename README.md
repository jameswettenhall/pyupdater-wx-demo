# pyupdater-wx-demo
Demo of self-updating wxPython application.

PyUpdater is based on PyInstaller, so most of the "pyupdater" command line
tools accept PyInstaller's command-line arguments in addition to PyUpdater's
command-line arguments.

The required Python modules for this demo can be installed with:

```pip install -r requirements.txt```

requirements.txt doesn't include wxPython.  It can be installed with:

```
    pip install -U --pre \
        -f https://wxpython.org/Phoenix/snapshot-builds/ \
        wxPython_Phoenix
```
or by downloading an installer from https://www.wxpython.org/

First, some semantics.  For a version like 1.3.5, '1' is the major version, '3'
is the minor version and '5' is the patch version.  When using PyUpdater, you
will sometimes see two additional numbers at the end of the version string,
e.g. "1.3.5.2.0".  The '2' is used to indicate a stable release (compared with
'1' for a beta release and '0' for an alpha release), and the final '0' is the
release number.

For updates which only change the patch version (e.g. from 1.3.5 to 1.3.7), an
application configured to use the PyUpdater client can automatically download
the new binary and restart itself.  This document will focus on this case.

This page lists the main steps to go through to get PyUpdater up and running:

http://www.pyupdater.org/usage-cli/

*Step 1 - Create Keypack*

```
$ pyupdater keys -c
Are you sure you want to continue?
[N/y]?y
Please enter app name - No Default Available
--> PyUpdaterWxDemo
You entered PyUpdaterWxDemo, is this correct?
[N/y]?y
[INFO] Keypack placed in cwd
```

*Step 2 - Copy Keypack*

Copy the keypack.pyu file you just generated inside your repo directory.  We
will delete the repo's copy of the keypack after it has been imported into
PyUpdater's config (because it contains a private key).

```cp keypack.pyu pyupdater-wx-demo/```

*Step 3 - Init Repo*

In this step, we'll need to supply the application name (PyUpdaterWxDemo) and a
URL to update from.  For the case of this demo, the URL of our Python Flask
file server will vary depending on what port is available, so we'll just enter
a placeholder URL for now:

```
$ pyupdater init
Please enter app name
[DEFAULT] -> PyUpdater App
Press Enter To Use Default
--> PyUpdaterWxDemo
You entered PyUpdaterWxDemo, is this correct?
[N/y]?y
Please enter your company or name
[DEFAULT] -> PyUpdater App
Press Enter To Use Default
--> Company Name
You entered Company Name, is this correct?
[N/y]?y
Enter a url to ping for updates. - No Default Available
--> http://www.example.com
You entered http://www.example.com, is this correct?
[N/y]?y
Would you like to add another url for backup?
[N/y]?n
Would you like to enable patch updates?
[Y/n]?y
Please enter the path to where pyupdater will write the client\_config.py file. You'll need to import this file to initialize the update process. 
Examples:

lib/utils, src/lib, src. 

Leave blank to use the current directory
[DEFAULT] -> pyupdater-wx-demo
Press Enter To Use Default
--> 
You entered pyupdater-wx-demo, is this correct?
[N/y]?y
[INFO] Creating pyu-data dir...
[INFO] Creating config dir
[INFO] Creating dir: /Users/james/Desktop/git/pyupdater-wx-demo/pyu-data
[INFO] Creating dir: /Users/james/Desktop/git/pyupdater-wx-demo/pyu-data/new
[INFO] Creating dir: /Users/james/Desktop/git/pyupdater-wx-demo/pyu-data/deploy
[INFO] Creating dir: /Users/james/Desktop/git/pyupdater-wx-demo/pyu-data/files
[WARNING] Version file not found
[INFO] Created new version file
[INFO] Creating new config file
[INFO] Saving Config
[INFO] Config saved
[INFO] Wrote client config
[INFO] Setup complete
```

*Step 4 - Import Keypack*

```
$ pyupdater keys --import
Are you sure you want to continue?
[N/y]?y
[INFO] Keypack import successfully
[INFO] Saving Config
[INFO] Config saved
[INFO] Wrote client config

$ rm keypack.pyu
```

*Step 5 - Integrate PyUpdater*

See run.py.


*Step 6 - Make Spec*

The binary executable can be built in two steps, the first of which is to
create a spec file (i.e. a reciped for constructing the final application
bundle).  On Windows, you can skip this skip, but on Mac OS X, you probably
want to customize the Info.plist added to the PyWxUpdateDemo.app bundle.

```
$ pyupdater make-spec --windowed run.py
[INFO] wrote /Users/james/Desktop/git/pyupdater-wx-demo/mac.spec
```

*Step 7 - Build*

```
$ cat wxupdatedemo/__init__.py 

$ pyupdater build --windowed --app-version 0.0.1 run.py 
...
[INFO] PyUpdaterWxDemo-mac-0.0.1.tar.gz has been placed in your new folder
```

OR

```
$ pyupdater make-spec --windowed run.py
[INFO] wrote /Users/james/Desktop/git/pyupdater-wx-demo/mac.spec
# Edit mac.spec...
$ pyupdater build --windowed --app-version 0.0.1 mac.spec 
...
[INFO] PyUpdaterWxDemo-mac-0.0.1.tar.gz has been placed in your new folder
```

*Step 7.5 Updating mac.spec*

On Mac OS X, you may wish to edit the SPEC file, in particular,
you may want to add NSHighResolutionCapable to the Info.plist
as described here: https://pythonhosted.org/PyInstaller/spec-files.html
i.e.
```
app = BUNDLE(exe,
         name='myscript.app',
         icon=None,
         bundle_identifier=None
         info_plist={
            'NSHighResolutionCapable': 'True'
            },
         )
```

*Steps 8 and 9 - Create patches and sign*

```
$ pyupdater pkg --process --sign
[INFO] Adding package meta-data to version manifest
[INFO] Moving packages to deploy folder
[INFO] Processing packages complete
[INFO] Signing packages...
[INFO] Adding sig to update data
[INFO] Created gzipped version manifest in deploy dir
[INFO] Created gzipped key file in deploy dir
[INFO] Signing packages complete
```

Change ```__version__``` to 0.0.2 in ```wxupdatedemo/__init__.py``` and repeat:
```
$ pyupdater build --windowed --app-version 0.0.2 run.py 
...
[INFO] PyUpdaterWxDemo-mac-0.0.2.tar.gz has been placed in your new folder

$ pyupdater pkg --process --sign
```

Now let's run the frozen application on Mac OS X and see if can detect and
apply the available update:
```
$ mkdir tmp
$ cp pyu-data/deploy/PyUpdaterWxDemo-mac-1.0.0.tar.gz tmp/
$ cd tmp/
$ tar zxvf PyUpdaterWxDemo-mac-1.0.0.tar.gz 
$ export PYUPDATER_FILESERVER_DIR=/Users/james/Desktop/git/pyupdater-wx-demo/pyu-data/deploy/
$ open PyUpdaterWxDemo.app/
$ cd PyUpdaterWxDemo.app/
$ Contents/MacOS/PyUpdaterWxDemo --debug
```

run.py can also be run directly (without freezing), with or without the --debug option.

Tests can be run with:

```python setup.py nosetests```

Troubleshooting
==============
1. If PyInstaller hangs while performing the operation:

Adding redirect Microsoft.VC90.MFC

See: http://stackoverflow.com/questions/40380721/pyinstaller-hangs-adding-redirect-microsoft-vc90-mfc

2. In some versions of PyInstaller, sys.exit (used by run.py's
DisplayVersionAndExit) can generate a misleading 'Failed to execute script run'
message when running the frozen app.  This message can usually be ignored:
https://github.com/pyinstaller/pyinstaller/issues/1869

3. One of the tests may fail on Windows if running without administrator
privileges, because PyInstaller doesn't seem to embed an appropriate manifest
into the EXE to tell the OS that privilege elevation is not required.
