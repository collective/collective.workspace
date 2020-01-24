# coding=utf-8
from Acquisition import aq_chain
from collective.workspace import workspaceMessageFactory as _
from collective.workspace.interfaces import IWorkspace
from zope.interface import directlyProvides
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


def find_workspace(context):
    while hasattr(context, "context"):
        context = context.context
    for context in aq_chain(context):
        workspace = IWorkspace(context, None)
        if workspace is not None:
            return workspace


def TeamGroupsVocabulary(context):
    workspace = find_workspace(context)
    # Membership in the auto_groups is determined automatically,
    # so we don't need to show them as explicit options.
    groups = set(workspace.available_groups.keys()) - set(workspace.auto_groups.keys())
    items = []
    for group in groups:
        items.append(SimpleTerm(group, group, _(group)))
    return SimpleVocabulary(items)


directlyProvides(TeamGroupsVocabulary, IVocabularyFactory)
