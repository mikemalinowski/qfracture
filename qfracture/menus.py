import qute
import collections

from . import constants


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences
class ElementMenu(qute.QMenu):

    # --------------------------------------------------------------------------
    def __init__(self, element, *args, **kwargs):
        super(ElementMenu, self).__init__(*args, **kwargs)

        self.element = element

        # -- Add the menu items from the plugins
        menu_dict = collections.OrderedDict()
        menu_dict.update(element.functionality())

        # -- Add the seed menu items
        menu_dict['-'] = None
        menu_dict['Copy Path'] = self.copyPath

        # -- Determine if we need to
        if constants.FAVOURITE_TAG in element.tags():
            menu_dict['Remove from Favourites'] = self.unmarkAsFavourite

        else:
            menu_dict['Add to Favourites'] = self.markAsFavourite

        # -- We list all the components of an element, so
        # -- build that structure up
        component_data = collections.OrderedDict()
        data_types = sorted(
            [
                component.data_type
                for component in element.components()
            ]
        )

        for data_type in data_types:
            component_data['[%s]' % data_type] = self.null

        # -- Expose it in a sub menu
        menu_dict['--'] = None
        menu_dict['Components'] = component_data

        # -- Use Qute to populate our menu based on the dictionary
        qute.menuFromDictionary(
            menu_dict,
            parent=self,
            icon_paths=[constants.RESOURCES]
        )

    # --------------------------------------------------------------------------
    def null(self):
        """
        A blank callable.
        """
        pass

    # --------------------------------------------------------------------------
    def copyPath(self):
        """
        Private function for exposing built-in functionality to the
        context menu.
        """
        clipboard = qute.QApplication.clipboard()
        clipboard.setText(self.element.identifier())

    # --------------------------------------------------------------------------
    def markAsFavourite(self):
        """
        Private function for exposing built-in functionality to the
        context menu.
        """
        self.element.tag(constants.FAVOURITE_TAG)

    # --------------------------------------------------------------------------
    def unmarkAsFavourite(self):
        """
        Private function for exposing built-in functionality to the
        context menu.
        """
        self.element.untag(constants.FAVOURITE_TAG)
