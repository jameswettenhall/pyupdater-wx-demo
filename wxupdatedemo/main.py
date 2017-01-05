"""
A simple wxPython application which displays its version number
in a static text widget on the application's main frame.
"""
import os
import sys
import wx

from wxupdatedemo import __version__
from wxupdatedemo.fileserver import ShutDownFileServer


class PyUpdaterWxDemoApp(wx.App):
    """
    A simple wxPython application which displays its version number
    in a static text widget on the application's main frame.
    """
    def __init__(self, fileServerPort, status):
        self.fileServerPort = fileServerPort
        self.status = status
        self.frame = None
        self.panel = None
        self.statusBar = None
        self.sizer = None
        wx.App.__init__(self, redirect=False)

    def OnInit(self):
        """
        Run automatically when the wxPython application starts.
        """
        self.frame = wx.Frame(None, title="PyUpdater wxPython Demo")
        self.frame.Bind(wx.EVT_CLOSE, self.OnCloseFrame)
        self.frame.SetSize(wx.Size(400, 100))
        self.statusBar = wx.StatusBar(self.frame)
        self.statusBar.SetStatusText(self.status)
        self.frame.SetStatusBar(self.statusBar)
        self.panel = wx.Panel(self.frame)
        self.sizer = wx.BoxSizer()
        self.sizer.Add(
            wx.StaticText(self.frame, label="Version %s" % __version__))
        self.panel.SetSizerAndFit(self.sizer)

        self.frame.Show()

        if hasattr(sys, "frozen") and \
                not os.environ.get('PYUPDATER_FILESERVER_DIR'):
            dlg = wx.MessageDialog(
                self.frame,
                "The PYUPDATER_FILESERVER_DIR environment variable "
                "is not set!", "PyUpdaterWxDemo File Server Error",
                wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()

        return True

    def OnCloseFrame(self, event):
        """
        Closing the main frame will cause the wxPython application to shut
        down.  We should terminate the file server process at this point.
        """
        if self.fileServerPort:
            ShutDownFileServer(self.fileServerPort)
        event.Skip()

    @staticmethod
    def Run(fileServerPort, status, mainLoop=True):
        """
        Create the app and run its main loop to process events.

        If being called by automated testing, the main loop
        won't be run and the app will be returned.
        """
        app = PyUpdaterWxDemoApp(fileServerPort, status)
        if mainLoop:
            app.MainLoop()
        return app
