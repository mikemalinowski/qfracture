"""
This is a plugin creator wizard to make it easy for users to generate
their own plugins without coding.
"""
import os
import sys
import qute
import fracture
import functools


# ------------------------------------------------------------------------------
def _get_resource(name):
    """
    This is a convinience function to get files from the resources directory
    and correct handle the slashing.

    :param name: Name of file to pull from the resource directory

    :return: Absolute path to the resource requested.
    """
    return os.path.join(
        os.path.dirname(__file__),
        '_res',
        name,
    ).replace('//', '/')


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences,PyPep8Naming
class ClassWizard(qute.QWizard):
    """
    This is the main wizard class which guides the user through the 
    plugin creation. 
    """

    # --------------------------------------------------------------------------
    def __init__(self, parent=None):
        super(ClassWizard, self).__init__(parent)

        self.setWizardStyle(self.ModernStyle)
        self.setWindowTitle('Project Setup')
        self.setWindowIcon(
            qute.QIcon(fracture.icon('fracture_65'))
        )

        self.setPixmap(
            self.WatermarkPixmap,
            _get_resource('wizard.png'),
        )

        qute.applyStyle(
            [
                'space',
                _get_resource('wizard.qss'),
            ],
            self,
        )

        # -- Add pages to the wizard
        self.addPage(DataRootsPage())
        self.addPage(PluginLocationsPage())

        self.savePage = SaveProjectPage()
        self.addPage(self.savePage)

    # --------------------------------------------------------------------------
    def updateScanProgress(self, info):
        """
        Triggered during a scan, and updates the ui
        """
        self.savePage.ui.scanOutput.setText(info)
        self.update()

    # --------------------------------------------------------------------------
    def accept(self):
        """
        Upon acceptence, we can generate a plugin from the template.
        """
        data_paths = self.field('exportDataPaths').split(';')
        plugin_paths = self.field('exportPluginPaths').split(';')
        save_location = self.field('saveLocation')

        project = fracture.create(
            project_path=save_location,
            plugin_locations=[path for path in plugin_paths if path]
        )

        # -- Tell the project where to look for data
        for location in data_paths:
            if location:
                project.add_scan_location(location)

        # -- Now we initiate a scan. This will cycle over all the
        # -- scan locations and scrape them for data
        project.scanned.connect(self.updateScanProgress)
        project.scan()

        super(ClassWizard, self).accept()


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences,PyPep8Naming,PyMethodMayBeStatic
class BasePage(qute.QWizardPage):

    # --------------------------------------------------------------------------
    def __init__(self, parent=None):
        super(BasePage, self).__init__(parent=parent)

        self.setLayout(qute.slimify(qute.QVBoxLayout()))

    # --------------------------------------------------------------------------
    def addLocation(self, list_widget, export_widget):
        """
        Generic add location callback function which pops up a browser and
        places the data into the given export widget.
        """
        # -- Sessions are given newest to oldest
        folder_path = qute.QFileDialog.getExistingDirectory(
            self,
            'Data Search Root',
        )
        if not folder_path:
            return

        folder_path = folder_path.replace('//', '/')

        # -- Add the item
        list_widget.addItem(folder_path)
        self.serialiseData(list_widget, export_widget)

    # --------------------------------------------------------------------------
    def removeLocation(self, list_widget, export_widget):
        """
        Convenience function for removing the selected entry from a list
        widget and re-serialising the data.
        """
        list_widget.takeItem(list_widget.currentRow())
        self.serialiseData(list_widget, export_widget)

    # --------------------------------------------------------------------------
    def serialiseData(self, list_widget, export_widget):
        """
        Convenience function for writing out the data from a list widget
        into a line edit.
        """
        # -- Serialise the data
        export_data = ''
        for idx in range(list_widget.count()):
            export_data += '%s;' % list_widget.item(idx).text()
            export_widget.setText(export_data)


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences
class DataRootsPage(BasePage):

    # --------------------------------------------------------------------------
    def __init__(self, parent=None):
        super(DataRootsPage, self).__init__(parent)

        # -- Load in our ui element
        self.ui = qute.loadUi(_get_resource('wizard_page_one.ui'))
        self.layout().addWidget(self.ui)

        self.ui.exportDataPaths.setVisible(False)

        # -- Register the field
        self.registerField('exportDataPaths', self.ui.exportDataPaths)

        self.ui.addSearchRootButton.clicked.connect(
            functools.partial(
                self.addLocation,
                self.ui.searchRoots,
                self.ui.exportDataPaths,
            )
        )

        self.ui.removeSearchRootButton.clicked.connect(
            functools.partial(
                self.removeLocation,
                self.ui.searchRoots,
                self.ui.exportDataPaths,
            )
        )


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences
class PluginLocationsPage(BasePage):

    # --------------------------------------------------------------------------
    def __init__(self, parent=None):
        super(PluginLocationsPage, self).__init__(parent)

        # -- Load in our ui element
        self.ui = qute.loadUi(_get_resource('wizard_page_two.ui'))
        self.layout().addWidget(self.ui)

        self.ui.exportPluginPaths.setVisible(False)

        self.registerField('exportPluginPaths', self.ui.exportPluginPaths)

        self.ui.addPluginLocationButton.clicked.connect(
            functools.partial(
                self.addLocation,
                self.ui.pluginLocations,
                self.ui.exportPluginPaths,
            )
        )

        self.ui.removePluginLocationButton.clicked.connect(
            functools.partial(
                self.removeLocation,
                self.ui.pluginLocations,
                self.ui.exportPluginPaths,
            )
        )


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences,PyPep8Naming
class SaveProjectPage(BasePage):

    # --------------------------------------------------------------------------
    def __init__(self, parent=None):
        super(SaveProjectPage, self).__init__(parent)

        # -- Load in our ui element
        self.ui = qute.loadUi(_get_resource('wizard_page_three.ui'))
        self.layout().addWidget(self.ui)

        # -- Register the field
        self.registerField(
            'saveLocation',
            self.ui.saveLocation,
        )

        self.ui.setSaveLocationButton.clicked.connect(
            self.setSaveLocation,
        )

    # --------------------------------------------------------------------------
    def setSaveLocation(self):

        # -- Browse for a file
        path, _ = qute.QFileDialog.getSaveFileName(
            self,
            dir='',
            filter='fracture (*.fracture)'
        )
        if not path:
            return None

        self.ui.saveLocation.setText(path.replace('//', '/'))


# ------------------------------------------------------------------------------
def show():
    _wizard = ClassWizard()
    _wizard.exec_()


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app = qute.qApp()
    wizard = ClassWizard()
    wizard.show()
    sys.exit(app.exec_())
