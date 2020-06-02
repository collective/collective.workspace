# coding=utf-8
from .interfaces import IHasWorkspace
from .interfaces import IWorkspace
from plone.indexer import indexer
from zope.interface import Interface


try:
    from Products.CMFPlone.utils import safe_nativestring
except ImportError:
    from collective.workspace._compat import safe_nativestring


@indexer(IHasWorkspace)
def workspace_members(self):
    workspace = IWorkspace(self)
    return set(map(safe_nativestring, workspace.members or []))


@indexer(Interface)
def null_indexer(self):
    raise AttributeError
