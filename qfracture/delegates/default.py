import qute
import fracture
import qfracture

import os


# ------------------------------------------------------------------------------
# noinspection PyUnresolvedReferences
class DefaultElementDelegate(qfracture.ElementDelegate):
    """
    This delegate is what we use by default if no other delegate
    is able to represent a piece of data
    """
    # -- Plugin Requirements
    name = 'Default Delegate'

    representing = [

    ]

    # -- Fonts
    NAME_FONT = qute.QFont('Ariel', 8, qute.QFont.Normal)
    DESC_FONT = qute.QFont('Ariel', 8, qute.QFont.StyleItalic)
    LARGE_NAME_FONT = qute.QFont('Ariel', 10, qute.QFont.Normal)

    # -- Brushes
    NAME_PEN = qute.QPen(qute.QColor(255, 255, 255))
    ACTIVE_NAME_PEN = qute.QPen(qute.QColor(255, 255, 255))
    DESC_PEN = qute.QPen(qute.QColor(255, 255, 255, 150))

    # -- Static Values
    BORDER = 5

    DEFAULT_ICON = fracture.icon('fracture_65')

    # --------------------------------------------------------------------------
    def __init__(self, element, parent=None):
        super(DefaultElementDelegate, self).__init__(element, parent)

        self.name = self.element.label()
        self.identifier = self.element.identifier()
        self.icon = self.element.icon()

    # --------------------------------------------------------------------------
    def paint(self, painter, option, index):

        # -- Add extra details for the selected item
        background_opacity = 0
        if option.state & qute.QStyle.State_Selected:
            background_opacity = 25
        elif option.state & qute.QStyle.State_MouseOver:
            background_opacity = 15

        painter.fillRect(
            option.rect,
            qute.QColor(
                255,
                255,
                255,
                background_opacity,
            )
        )

        # -- Draw the main header
        painter.setFont(self.NAME_FONT)
        painter.setPen(self.NAME_PEN)

        # -- Draw the main entry name
        painter.drawText(
            option.rect.x() + self._SIZE_HINT + self.BORDER,
            option.rect.y() + 15,
            self.name,
        )

        # -- Define the descriptions parameters
        painter.setOpacity(0.5)
        painter.setFont(self.DESC_FONT)
        painter.setPen(self.DESC_PEN)

        # -- Draw the descriptive text
        painter.drawText(
            option.rect.x() + self._SIZE_HINT + self.BORDER,
            option.rect.y() + 30,
            self.identifier,
        )
        painter.setOpacity(1)

        # -- If we have an icon, use it (providing it exists)
        # -- otherwise we fall back to our default icon
        icon = self.icon
        if not icon or not os.path.exists(icon):
            icon = self.DEFAULT_ICON

        px = qute.QPixmap(icon).scaled(
            self._SIZE_HINT,
            self._SIZE_HINT,
            mode=qute.Qt.SmoothTransformation,
        )

        # -- Draw the icon
        painter.drawPixmap(
            qute.QRect(
                option.rect.x(),
                option.rect.y(),
                self._SIZE_HINT,
                self._SIZE_HINT,
            ),
            px,
        )

    # --------------------------------------------------------------------------
    def sizeHint(self, option, index):
        return qute.QSize(1, self._SIZE_HINT)
