"""
This is the main module for the qFracture Interface
"""
import re
import os
import qute
import fracture
import scribble
import factories
import subprocess

from . import menus
from . import wizard
from . import browser
from . import constants


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences,PyPep8Naming
class FractureUi(qute.QWidget):
    """
    This is a generic Ui Element for interacting with 
    seed.
    """

    _TAG_SPLIT = re.compile('[, ]')

    # --------------------------------------------------------------------------
    def __init__(self,
                 project_path,
                 style='space',
                 environment_id='qfracture',
                 parent=None):
        super(FractureUi, self).__init__(parent=parent)
        
        # -- Store the environment id, this is what we use to 
        # -- store and apply settings with
        self.environment_id = environment_id
        
        # -- Setup our window properties, ensuring it has an icon etc
        self.setWindowIcon(qute.QIcon(fracture.icon('fracture_65_black')))
        self.setWindowTitle('Fracture')

        # -- Apply a css stylesheet to our ui to make it a little
        # -- less bland!
        qute.applyStyle(
            [
                style,
                constants.UI_STYLE,
            ],
            self,
        )

        # -- Define the delegate accessors once the seed it set
        self.delegates = None
        self._potential_delegates = list()

        # -- Get the default display delegate from the factory
        # -- so we can utilise it if no other delegates are matched
        self._default_delegate = None

        # -- Load in our ui file
        self.ui = qute.loadUi(constants.UI_FILE)

        # -- Add the ui to the layout of our widget
        self.setLayout(qute.slimify(qute.QVBoxLayout()))
        self.layout().addWidget(self.ui)

        # -- Define the variable where we will hold the currently
        # -- active fracture instance
        self.project = None

        # -- Load in our settings
        settings = scribble.get(self.environment_id)

        # -- Set the seed to the current item - this ensures
        # -- the ui is all up to date
        self.setProject(project_path or settings.get('last_loaded', None))

        # -- Set the window geometry if we have the settings
        self.window().setGeometry(
            *settings.get(
                'geometry',
                [
                    300,
                    300,
                    400,
                    400,
                ]
            )
        )

        # -- Hook up our signals and slots to ensure the interaction
        # -- of the UI works as the user would expect
        self.ui.tags.returnPressed.connect(self.query)
        self.ui.tags.textChanged.connect(self.query)
        self.ui.browseList.itemRequiresDelegate.connect(self.assignDelegate)

        self.ui.addScanLocation.clicked.connect(self.addScanLocation)
        self.ui.removeScanLocation.clicked.connect(self.removeScanLocation)

        self.ui.addPluginLocation.clicked.connect(self.addPluginLocation)
        self.ui.removePluginLocation.clicked.connect(self.removePluginLocation)

        self.ui.addIgnorePattern.clicked.connect(self.addIgnorePattern)
        self.ui.removeIgnorePattern.clicked.connect(self.removeIgnorePattern)

        self.ui.setupProject.clicked.connect(self.initiateWizard)
        self.ui.loadProject.clicked.connect(self.loadProject)
        self.ui.launchSystemTray.clicked.connect(self.launchSystemTray)

        # -- Hook up the context menu rules
        self.ui.results.setContextMenuPolicy(qute.Qt.CustomContextMenu)
        self.ui.results.customContextMenuRequested.connect(
            self.itemContext,
        )

        # -- Initiate a starting query - which will display
        # -- any items marked as favourites
        self.query()

    # --------------------------------------------------------------------------
    def launchSystemTray(self):
        """
        This will launch a standalone system tray scanner for the currently
        active project.

        :return:
        """
        subprocess.Popen(
            [
                'python',
                os.path.join(
                    os.path.dirname(__file__),
                    'tray',
                    'core.py',
                ),
                self.project.identifier,
            ],
        )

    # --------------------------------------------------------------------------
    def loadProject(self):
        """
        Prompts the user for a fracture project file and then loads
        that project.

        :return:
        """
        load_path, _ = qute.QFileDialog.getOpenFileName(
            self,
            'Select Fracture Project',
            '',
            'fracture (*.fracture)'
        )

        if load_path:
            self.setProject(load_path)

    # --------------------------------------------------------------------------
    def getDelegate(self, element):
        """
        Private method for returning the delegate to be used by 
        the given DataElement
        
        :param element: DataElement to be represented
        :type element: DataElement
        
        :return: ElementDelegate
        """
        for delegate in self._potential_delegates:
            for component in element.components():
                if str(component) in delegate.representing:
                    return delegate

        return self._default_delegate

    # --------------------------------------------------------------------------
    # noinspection PyUnusedLocal
    def query(self, *args, **kwargs):
        """
        This will initiate a query, populating the results list based
        on the tags given in the tag line edit.
         
        :return: 
        """
        if not self.project:
            return

        # -- Run a query from Seed, giving all the tags in the
        # -- tag line edit
        results = self.project.find(
            [
                tag
                for tag in self._TAG_SPLIT.split(self.ui.tags.text())
                if tag
            ] or ['$(fav)'],
            limit=self.ui.searchLimit.value()
        )

        # -- Clear the current view before we populate it
        # -- over again
        self.ui.results.clear()

        # -- Start cycling over our results
        for result in results:
            result = self.project.get(result)
            if not result:
                continue

            # -- Create a widget item and store our data element
            # -- within it
            item = qute.QListWidgetItem()

            # -- Setup the tooltip
            item.setToolTip(
                'Name: %s\nType: [%s]\n Path: %s' % (
                    result.label(),
                    str(result),
                    result.identifier(),
                ),
            )

            # -- Add the result to the list
            self.ui.results.addItem(item)

            item.element = result

            self.assignDelegate(item, self.ui.results)

    # --------------------------------------------------------------------------
    def assignDelegate(self, item, list_widget):
        """
        Assigns the delegeate to the item based on what components are
        applied to it.

        :param item: QListWidget item (with a DataElement instance bound to
            its .element property).

        :return: None
        """
        # -- Assign the delegate to the item
        list_widget.setItemDelegateForRow(
            list_widget.row(item),
            self.getDelegate(item.element)(item.element, parent=list_widget),
        )

    # --------------------------------------------------------------------------
    def setProject(self, project_path):
        """
        This will set the seed instance for the ui. A new Seed instance
        will be generated, and providing the identifier loads successfully
        the ui will be updated to reflect the change.
        
        :param project_path: Data Source identifier
        :type project_path: str
        
        :return: None 
        """
        if not project_path or not os.path.exists(project_path):
            return

        # -- Re-assign the project property
        self.project = fracture.load(project_path)

        # -- Clear our current project specific data ui elements
        self.ui.scanLocations.clear()
        self.ui.ignorePatterns.clear()
        self.ui.pluginLocations.clear()

        # -- Our plugin locations may be None, in which case
        # -- switch them to an empty list
        plugin_locations = self.project.plugin_locations() or list()

        # -- Populate our data ui elements
        for location in self.project.plugin_locations():
            self.ui.pluginLocations.addItem(location)

        for location in self.project.scan_locations():
            self.ui.scanLocations.addItem(location)

        for pattern in self.project.skip_regexes():
            self.ui.ignorePatterns.addItem(pattern)

        # -- Create a factory to hold all our delegate plugins. Delegates
        # -- allow per-data types to be drawn differently.
        self.delegates = factories.Factory(
            abstract=ElementDelegate,
            plugin_identifier='name',
            versioning_identifier='version',
            paths=plugin_locations + [constants.BUILTIN_PLUGIN_DIR],
        )
        
        # -- Add our bespoke delegates to the factory
        self.delegates.add_path(
            os.path.join(
                os.path.dirname(__file__),
                'delegates',
            ),
        )

        # -- As a matter of optimisation, we sort these plugins
        # -- by priority only once.
        self._potential_delegates = sorted(
            self.delegates.plugins(),
            key=lambda p: p.priority,
        )

        self._default_delegate = self.delegates.request('Default Delegate')

        # -- Set the project for our browse list
        self.ui.browseList.setProject(self.project)
        self.ui.browseList.populate()

        # -- Update the window title
        self.window().setWindowTitle(
            'Seed : %s' % os.path.basename(project_path).split('.')[0],
        )
        # -- Now we store the fact that this is the last loaded
        # -- project
        settings = scribble.get(self.environment_id)
        settings['last_loaded'] = project_path
        settings.save()

        # -- Log the switch
        fracture.log.info('Switched Project : %s' % project_path)

    # --------------------------------------------------------------------------
    def addScanLocation(self):
        """
        This will prompt for a new scan location, and providing the user
        hits ok, the location will be added to seed.
        
        :return: None 
        """
        # -- Prompt for the search location
        location, ok = qute.QInputDialog.getText(
            None,
            'Add Scan Location',
            'Enter location for scanning'
        )

        if not ok:
            return

        self.project.add_scan_location(location)
        self.ui.scanLocations.addItem(location)

    # --------------------------------------------------------------------------
    def removeScanLocation(self):
        """
        This will remove the currently selected scan location from the 
        seed instance.
        
        :return: None 
        """
        # -- Prompt for the search location
        result = qute.QMessageBox.question(
                self,
                'Remove Scan Location',
                'Are you sure you want to remove the scan location : %s' % (
                    self.ui.scanLocations.currentText()
                ),
                qute.QMessageBox.Yes,
                qute.QMessageBox.No,
            )

        if result != qute.QMessageBox.Yes:
            return

        self.project.remove_scan_location(
            self.ui.scanLocations.currentText(),
        )
        self.ui.scanLocations.removeItem(self.ui.scanLocations.currentIndex())

    # --------------------------------------------------------------------------
    def addPluginLocation(self):
        """
        This will prompt for a new scan location, and providing the user
        hits ok, the location will be added to seed.

        :return: None
        """
        # -- Sessions are given newest to oldest
        location = qute.QFileDialog.getExistingDirectory(
            self,
            'Pluigin Location',
        )

        if not location:
            return

        location = location.replace('//', '/')

        self.project.add_plugin_location(location)
        self.ui.pluginLocations.addItem(location)

    # --------------------------------------------------------------------------
    def removePluginLocation(self):
        """
        This will remove the currently selected scan location from the
        seed instance.

        :return: None
        """
        # -- Prompt for the search location
        result = qute.QMessageBox.question(
            self,
            'Remove Plugin Location',
            'Are you sure you want to remove the plugin location : %s' % (
                self.ui.pluginLocations.currentText()
            ),
            qute.QMessageBox.Yes,
            qute.QMessageBox.No,
        )

        if result != qute.QMessageBox.Yes:
            return

        self.project.remove_plugin_location(
            self.ui.pluginLocations.currentText(),
        )
        self.ui.pluginLocations.removeItem(self.ui.pluginLocations.currentIndex())

    # --------------------------------------------------------------------------
    def addIgnorePattern(self):
        """
        This will prompt the user for a new ignore pattern, and providing
        the user hits ok, the patter will be added to the seed instance.
        
        :return: None 
        """
        # -- Prompt for the search location
        pattern, ok = qute.QInputDialog.getText(
            None,
            'Add Ignore Pattern',
            'Enter pattern to add'
        )

        if not ok:
            return

        self.project.add_skip_regex(pattern)
        self.ui.ignorePatterns.addItem(pattern)

    # --------------------------------------------------------------------------
    def removeIgnorePattern(self):
        """
        This will remove the currently selected ignore pattern and remove
        it from the seed instance.
        
        :return: None 
        """
        # -- Prompt for the search location
        result = qute.QMessageBox.question(
                self,
                'Remove Ignore Pattern',
                'Are you sure you want to remove the pattern : %s' % (
                    self.ui.ignorePatterns.currentText()
                ),
                qute.QMessageBox.Yes,
                qute.QMessageBox.No,
            )

        if result != qute.QMessageBox.Yes:
            return

        self.project.remove_skip_regex(
            self.ui.ignorePatterns.currentText(),
        )
        self.ui.ignorePatterns.removeItem(self.ui.ignorePatterns.currentIndex())

    # --------------------------------------------------------------------------
    def itemContext(self, pos):
        """
        This will inspect whether there is an item under the mouse, and if
        one is found it will be queried for any actions, and all seed actions
        will be bound to it and a menu generated. 
        
        This is the function which exposes actions to the user.
        
        :param pos: QPoint
         
        :return: None 
        """
        # -- Get the item at the event position
        item = self.ui.results.itemAt(pos)

        # -- If there is no item at the mouse position
        # -- then we simply return
        if not item:
            return

        # -- Create the menu
        menu = menus.ElementMenu(
            element=item.element,
            parent=self
        )

        # -- Popup the menu
        menu.exec_(qute.QCursor().pos())

    # --------------------------------------------------------------------------
    # noinspection PyUnusedLocal
    def resizeEvent(self, event):
        """
        Switch between North and west as the user resizes the panel.
        """

        # -- Store the current window size in our scribble settings
        window = self.window()
        settings = scribble.get(self.environment_id)
        settings['geometry'] = [
            window.pos().x() + 7,
            window.pos().y() + 32,
            window.width(),
            window.height(),
        ]
        settings.save()

    # --------------------------------------------------------------------------
    def initiateWizard(self):
        """
        The wizard gives a guide interface to creating a new fracture project
        """
        # -- Instance the wizard and block
        wizard_window = wizard.ClassWizard()
        wizard_window.exec_()

        # -- Now that we're done, get the save location
        new_project_path = wizard_window.field('saveLocation')

        # -- Providing the save location is valid, lets set the project
        if new_project_path:
            self.setProject(new_project_path)


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences,PyPep8Naming
class ElementDelegate(qute.QStyledItemDelegate):
    """
    This is the main Ui Delegate abstract. All delegates must
    inherit from this.
    """
    name = 'AbstractDelegate'

    # -- Version attribute is used for overriding
    # -- a delegate
    version = 1

    # -- Priority is used to determine importance, as the
    # -- ui will take the first matched item. The higher the
    # -- number the higher importance it has
    priority = 0

    # -- This allows you to specify a list of data types your
    # -- delegate can represent.
    # -- Note, if you leave this value as None on your re-implementation
    # -- then your delegate will override the default delegate.
    representing = [

    ]

    # -- Tracker for icon size
    _SIZE_HINT = 40

    # --------------------------------------------------------------------------
    def __init__(self, element, parent=None):
        super(ElementDelegate, self).__init__(parent)

        self.element = element

    # --------------------------------------------------------------------------
    # noinspection PyUnusedLocal
    def paint(self, painter, option, index):
        pass

    # --------------------------------------------------------------------------
    # noinspection PyUnusedLocal
    def sizeHint(self, option, index):
        return qute.QSize(1, self._SIZE_HINT)


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences
def launch(project_path=None, blocking=True):

    q_app = qute.qApp()

    # -- Create a window and embed our widget into it
    widget = FractureUi(
        project_path=project_path,
    )
    window = qute.QMainWindow(parent=qute.mainWindow())

    # -- Update the geometry of the window to the last stored
    # -- geometry
    window.setGeometry(widget.geometry())
    window.setCentralWidget(widget)

    # -- Set the window properties
    title = 'Fracture : '

    if widget.project:
        title += os.path.basename(widget.project.identifier).split('.')[0]

    window.setWindowTitle(title)
    window.setWindowIcon(
        qute.QIcon(
            fracture.icon('fracture_65'),
        ),
    )

    # -- Show the ui, and if we're blocking call the exec_
    window.show()

    if blocking:
        q_app.exec_()


# ------------------------------------------------------------------------------
# -- Register our custom widgets which are used to override
# -- the widgets in the ui file
try:
    # noinspection PyUnresolvedReferences
    loader = qute.QtUiTools.QUiLoader()
    loader.registerCustomWidget(browser.FractureListWidget)

except Exception:
    pass
