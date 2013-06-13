from .interfaces import IHasWorkspace
from .interfaces import IWorkspace
from plone.indexer import indexer
from zope.interface import Interface


@indexer(IHasWorkspace)
def workspace_members(self):
    workspace = IWorkspace(self)
    return set(workspace.members)


@indexer(Interface)
def null_indexer(self):
    raise AttributeError
