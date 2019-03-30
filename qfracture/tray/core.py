"""

"""
import os
import sys
import qute
import fracture
import functools


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences,PyPep8Naming
class FractureTray(qute.QSystemTrayIcon):

    def __init__(self,
                 project_path,
                 auto_scan=False,
                 interval=5,
                 *args,
                 **kwargs):
        super(FractureTray, self).__init__(*args, **kwargs)

        # -- Store the fracture identifier we're responsible for
        self.project_path = project_path
        self.auto_scan = auto_scan
        self.interval = interval

        # -- Store the fracture instance we will use for scanning
        self.project = fracture.load(project_path=project_path)

        # -- We will use this to hold a thread from
        # -- which we will carry out our scanning
        self.scan_thread = None

        # -- Define our context menu. We will update this whenever
        # -- the user requests the menu
        self.menu = qute.QMenu()
        self.setContextMenu(self.menu)

        # -- Set the icon of the tray item. We request
        # -- this resource from fracture directly
        self.setIcon(qute.QIcon(fracture.icon('fracture_65')))

        # -- Create the timer object which we will use
        # -- to define when a scan will occur
        self.timer = qute.QTimer()
        self.timer.setInterval(self.interval * 1000)

        # -- If we're set to auto scan, then start a scan
        # -- immediately
        if self.auto_scan:
            self.scan()
            self.timer.start()

        # -- Ensure that when the timer trickles down
        # -- we begin a scan
        self.timer.timeout.connect(self.scan)

        # -- Hook up signals and slots. We use this signal to generate
        # -- the menu on-demand. This way the data is always correct at
        # -- the point in time when the user requests it
        self.activated.connect(self.generateMenu)

    # --------------------------------------------------------------------------
    def scan(self):
        """
        This will trigger a scan providing there is not a scan currently
        in progress. 
        """
        if not self.scan_thread:

            # -- Create the new scan thread
            self.scan_thread = ScanThread(self.project)

            # -- Ensure it clears itself once its finished, and
            # -- initiate its start.
            self.scan_thread.finished.connect(self.clear_scan)
            self.scan_thread.start()

    # --------------------------------------------------------------------------
    def clear_scan(self):
        """
        This is called whenever a scan is complete. This performs any
        object clean up.
        """
        self.scan_thread = None

    # --------------------------------------------------------------------------
    def generateMenu(self):
        """
        This will update the contents of the menu to be reflective of the
        users current settings. 
        """
        # -- Clear the current menu
        self.menu.clear()

        # -- Add an item which is here to show the identifier as well
        # -- as the scan status
        action = qute.QAction(
            '%s [%s]' % (
                os.path.basename(self.project_path).split('.')[0],
                'Scanning' if self.scan_thread else 'Idle',
            ),
            self.menu,
        )
        self.menu.addAction(action)

        # -- Add our seperator
        self.menu.addSeparator()

        # -- Add actions to enable/disable auto scan
        tag = 'Disable' if self.auto_scan else 'Enable'

        action = qute.QAction(
            '%s Auto Scan' % tag,
            self.menu,
        )

        # -- Connect the signal event
        action.triggered.connect(
            functools.partial(
                self.set_auto_scan,
                not self.auto_scan
            )
        )

        # -- Add the action
        self.menu.addAction(action)

        # -- Add the time between scan item
        action = qute.QAction(
            'Set Interval (%s)' % self.interval,
            self.menu
        )

        action.triggered.connect(
            functools.partial(
                self.set_time_between_scan,
            )
        )

        # -- Add the item
        self.menu.addAction(action)

        # -- Add our seperator
        self.menu.addSeparator()

        action = qute.QAction(
            'Scan',
            self.menu,
        )
        action.triggered.connect(self.scan)
        self.menu.addAction(action)

        # -- Add our seperator
        self.menu.addSeparator()

        # -- Add our exit option
        action = qute.QAction('Exit', self.menu)
        action.triggered.connect(sys.exit)
        self.menu.addAction(action)

        # -- Regenerate the menu
        self.setContextMenu(self.menu)

    # --------------------------------------------------------------------------
    def set_auto_scan(self, value):
        """
        This will change the auto scan setting.
        
        :param value: The value to switch to 
        """
        self.auto_scan = value

        if self.auto_scan:
            self.timer.start()

        else:
            self.timer.stop()

    # --------------------------------------------------------------------------
    def set_time_between_scan(self):
        """
        This allows the user to tailor how long to run between 
        scans 
        """
        value, ok = qute.QInputDialog.getInt(
            None,
            'Time (in minutes) between scans',
            'This is minimum time between scans',
            self.interval,
            minValue=1,
            maxValue=10000,
            step=1,
        )

        if not ok:
            return

        # -- Update our interval variable and apply it to the
        # -- timer
        self.interval = value
        self.timer.stop()
        self.timer.setInterval(self.interval * 1000)

        if self.auto_scan:
            self.timer.start()


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences
class ScanThread(qute.QThread):
    """
    All our scanning is handled in a thread to prevent the rest
    of the ui elements from being blocked.
    """
    # --------------------------------------------------------------------------
    def __init__(self, fracture_project):
        super(ScanThread, self).__init__()
        self.fracture_project = fracture_project

    # --------------------------------------------------------------------------
    def run(self):
        self.fracture_project.scan()


# ------------------------------------------------------------------------------
def launch(fracture_project, auto_scan=False, interval=10):
    """
    This is a convinence entrypoint to start the system tray
    application.
    
    :param fracture_project: The absolute path to the seed project
    :param auto_scan: This decides whether it will auto scan by default
    :param interval: This defines the default time between scans 
    """
    q_app = qute.qApp([])
    q_app.setQuitOnLastWindowClosed(False)

    tray = FractureTray(
        fracture_project,
        auto_scan=auto_scan,
        interval=interval,
    )

    tray.show()

    q_app.exec_()


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    launch(*sys.argv[1:])
