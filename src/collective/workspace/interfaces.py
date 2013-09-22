from zope.interface import Interface


class IHasWorkspace(Interface):
    """Marker for team workspaces."""


class IWorkspace(Interface):
    """Interface for interacting with an item's workspace features."""


class IRosterView(Interface):
    """Marker for display view of a roster."""
