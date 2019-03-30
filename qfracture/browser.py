"""
The browser aims to give a more guide exploration mechanism, where the
user can traverse up and down within search locations, finding DataElements
within.
"""
import os
import qute

from . import menus


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences,PyPep8Naming
class FractureListWidget(qute.QListWidget):
    """
    This is a specifically designed list widget which exposes navigational
    elements at the top of the list to allow for scan location traversal along
    with the exposure of DataElements at the bottom of the list which can be
    found within the given search root.

    It essentially forms a kind of file browser which is not restricted
    specifically to folder/files but instead it is fed from the scan plugins.

    This makes it possible to combine the results of things like folder queries
    as well as source control queries or http queries.
    """

    # -- This is the maximum number of entries we show any any
    # -- one time for upward navigation.
    MAX_ABOVE = 2
    
    itemRequiresDelegate = qute.Signal(object, object)
    
    # --------------------------------------------------------------------------
    def __init__(self, parent=None):
        super(FractureListWidget, self).__init__(parent=parent)

        # -- This will be the fracture project we're interacting with. This
        # -- is set through the setProject method.
        self.project = None

        # -- Track the current location as the user clicks through
        self._current_location = None

        # -- Ensure we update the ui whenever the user asks to
        # -- center on an item
        self.itemClicked.connect(self.centerOn)

        self.setContextMenuPolicy(qute.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(
            self.itemContext,
        )

    # --------------------------------------------------------------------------
    def setProject(self, project):
        """
        Sets the active fracture project, and gives reference to the parent
        widget - which is expected to be a FractureUi instance.

        :param project: fracture.Project

        :return:
        """
        self.project = project

    # --------------------------------------------------------------------------
    def centerOn(self, item):
        """
        Triggered when the user clicks on
        :param item:
        :return:
        """
        # -- Check whether this is a valid item to be centered on
        if not hasattr(item, 'identifier'):
            return

        # -- If there is no change, do nothing
        if self._current_location == item.identifier:
            return

        # -- Store the current location and ask the view to
        # -- repopulate
        self._current_location = item.identifier
        self.populate()

    # --------------------------------------------------------------------------
    def populate(self):
        """
        Updates the view, building the navigation elements first before
        drawing the results.

        :return: None
        """
        # -- Clear the current view
        self.clear()

        # -- If we do not have a current location then we just
        if not self._current_location:
            for root in self.project.scan_locations():
                self._addDelegatedItem(root, RootAccessDelegate)

        else:

            # -- Add an accessor to the root locations
            self._addDelegatedItem(None, RootAccessDelegate, '...top...')

            # -- Get a list of all the items above and below
            above_items, below_items = self.project.explore(
                self._current_location,
            )

            # -- Add them in reverse, so it makes top down sense
            for item in reversed(above_items[:self.MAX_ABOVE]):
                self._addDelegatedItem(item, AboveDelegate)

            # -- If we have a current location we add that in.
            self._addDelegatedItem(self._current_location, CurrentDelegate)

            # -- Now we need to add the items below
            for item in below_items:
                self._addDelegatedItem(item, BelowDelegate)

            # -- Get the immediate identifiers
            elements = self.project.scan(
                self._current_location,
                recursive=False,
                full=False
            )

            for item in elements:

                result = self.project.get(item)

                if not result:
                    continue

                # -- Create a widget item and store our data element
                # -- within it
                item = qute.QListWidgetItem()

                # -- Assign the element composite to the item
                item.element = result

                # -- Add the result to the list
                self.addItem(item)

                # -- Declare that this item is ready for any delegates
                # -- to be bound for it
                self.itemRequiresDelegate.emit(item, self)

    # --------------------------------------------------------------------------
    def itemContext(self, pos):
        """
        This will inspect whether there is an item under the mouse, and if
        one is found it will be queried for any actions, and all fractyre 
        actions will be bound to it and a menu generated.

        This is the function which exposes actions to the user.

        :param pos: QPoint

        :return: None
        """
        # -- Get the item at the event position
        item = self.itemAt(pos)

        # -- If there is no item at the mouse position
        # -- then we simply return
        if not item or not hasattr(item, 'element'):
            return

        # -- Create the menu
        menu = menus.ElementMenu(
            element=item.element,
            parent=self
        )

        # -- Popup the menu
        menu.exec_(qute.QCursor().pos())

    # --------------------------------------------------------------------------
    def _addDelegatedItem(self, identifier, delegate, label=None):
        """
        This is a convenience function for added a list widget item with a
        specified delegate, as this is a proccess done multiple times during
        the populate method.

        :param identifier: DataElement Identifier
        :param delegate: Delegate to assign
        :param label: Optional label to assign to the delegate

        :return: None
        """
        # -- Add an accessor to the root locations
        root_access_item = qute.QListWidgetItem('current')
        root_access_item.identifier = identifier

        # -- Add the result to the list
        self.addItem(root_access_item)

        # -- Assign the delegate to the item
        self.setItemDelegateForRow(
            self.row(root_access_item),
            delegate(label or identifier, parent=self),
        )


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences,PyPep8Naming
class DirectionalDelegate(qute.QStyledItemDelegate):
    """
    This delegate is what we use by default if no other delegate
    is able to represent a piece of data
    """

    # -- Fonts
    NAME_FONT = qute.QFont('Ariel', 8, qute.QFont.Normal)
    DESC_FONT = qute.QFont('Ariel', 8, qute.QFont.StyleItalic)
    LARGE_NAME_FONT = qute.QFont('Ariel', 10, qute.QFont.Normal)

    # -- Brushes
    BG_COLOR = [109, 214, 255]
    NAME_PEN = qute.QPen(qute.QColor(255, 255, 255))
    BLACK_PEN = qute.QPen(qute.QColor(0, 0, 0))
    ACTIVE_NAME_PEN = qute.QPen(qute.QColor(255, 255, 255))
    DESC_PEN = qute.QPen(qute.QColor(255, 255, 255, 150))

    # -- Static Values
    BORDER = 5

    SIZE_HINT = 25
    DEFAULT_ICON = os.path.join(
        os.path.dirname(__file__),
        '_res',
        'above.png',
    )

    # --------------------------------------------------------------------------
    def __init__(self, identifier, parent=None):
        super(DirectionalDelegate, self).__init__(parent)
        self.identifier = identifier

    # --------------------------------------------------------------------------
    # noinspection PyUnusedLocal
    def paint(self, painter, option, index):

        # -- Add extra details for the selected item
        background_opacity = 50
        if option.state & qute.QStyle.State_MouseOver:
            background_opacity = 100
        
        # -- Draw the background
        painter.fillRect(
            option.rect,
            qute.QColor(
                self.BG_COLOR[0],
                self.BG_COLOR[1],
                self.BG_COLOR[2],
                background_opacity,
            )
        )

        # -- Draw the main header
        painter.setFont(self.NAME_FONT)
        painter.setPen(self.NAME_PEN)

        # -- Draw the main entry name
        painter.drawText(
            option.rect.x() + self.SIZE_HINT + self.BORDER,
            option.rect.y() + 15,
            os.path.basename(self.identifier),
        )

        # -- If we have an icon, use it (providing it exists)
        # -- otherwise we fall back to our default icon
        # icon = self.icon
        # if not icon or not os.path.exists(icon):
        icon = self.DEFAULT_ICON

        px = qute.QPixmap(icon).scaled(
            self.SIZE_HINT,
            self.SIZE_HINT,
            mode=qute.Qt.SmoothTransformation,
        )

        # -- Draw the icon
        painter.drawPixmap(
            qute.QRect(
                option.rect.x(),
                option.rect.y(),
                self.SIZE_HINT,
                self.SIZE_HINT,
            ),
            px,
        )

        painter.setPen(self.BLACK_PEN)
        # -- Finally, draw the border
        painter.drawRect(
            option.rect,
        )

    # --------------------------------------------------------------------------
    # noinspection PyUnusedLocal
    def sizeHint(self, option, index):
        return qute.QSize(1, self.SIZE_HINT)


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences
class BelowDelegate(DirectionalDelegate):
    """
    This delegate is what we use by default if no other delegate
    is able to represent a piece of data
    """
    DEFAULT_ICON = os.path.join(
        os.path.dirname(__file__),
        '_res',
        'below.png',
    )

    BG_COLOR = [
        109,
        214,
        255,
    ]


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences
class AboveDelegate(DirectionalDelegate):
    """
    This delegate is what we use by default if no other delegate
    is able to represent a piece of data
    """
    DEFAULT_ICON = os.path.join(
        os.path.dirname(__file__),
        '_res',
        'above.png',
    )

    BG_COLOR = [
        50,
        50,
        50,
    ]


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences
class CurrentDelegate(DirectionalDelegate):
    """
    This delegate is what we use by default if no other delegate
    is able to represent a piece of data
    """
    DEFAULT_ICON = os.path.join(
        os.path.dirname(__file__),
        '_res',
        'current.png',
    )

    BG_COLOR = [
        100,
        255,
        100,
    ]


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences
class RootAccessDelegate(DirectionalDelegate):
    """
    This delegate is what we use by default if no other delegate
    is able to represent a piece of data
    """
    DEFAULT_ICON = os.path.join(
        os.path.dirname(__file__),
        '_res',
        'search.png',
    )

    BG_COLOR = [
        100,
        100,
        100,
    ]
