from zope.i18nmessageid import MessageFactory
from zope.interface import Interface

_ = MessageFactory('collective.workspace')


class IHasWorkspace(Interface):
    """Marker for team workspaces."""


class IWorkspace(Interface):
    """Interface for interacting with an item's workspace features."""


class IRosterView(Interface):
    """Marker for display view of a roster."""
