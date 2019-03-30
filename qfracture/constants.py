"""
This holds a series of constant variables utilised across multiple
functions and modules.
"""
import os


# ------------------------------------------------------------------------------
# -- This is the location of our static resources
RESOURCES = os.path.join(
    os.path.dirname(__file__),
    '_res',
)


# ------------------------------------------------------------------------------
# -- This is the ui file (path) which describes the majority
# -- of the static interface
UI_FILE = os.path.join(
    RESOURCES,
    'fracture.ui',
)

UI_STYLE = os.path.join(
    RESOURCES,
    'qfracture.css',
)


# ------------------------------------------------------------------------------
# -- This is a fracture ui tag used to allow users to mark
# -- data elements as favourites
FAVOURITE_TAG = '$(fav)'


# ------------------------------------------------------------------------------
BUILTIN_PLUGIN_DIR = os.path.join(
    os.path.dirname(__file__),
    'delegates',
)