from collective.workspace.interfaces import IWorkspace
from zope.interface import directlyProvides
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary


def find_workspace(context):
    while hasattr(context, 'context'):
        context = context.context
    for context in reversed(context.aq_chain):
        workspace = IWorkspace(context, None)
        if workspace is not None:
            return workspace


def TeamGroupsVocabulary(context):
    workspace = find_workspace(context)
    # Membership in the Members group is implied by
    # inclusion in the roster, so we don't need to show
    # it as an explicit option.
    groups = set(workspace.available_groups.keys()) - set([u'Members'])
    return SimpleVocabulary.fromValues(sorted(groups))
directlyProvides(TeamGroupsVocabulary, IVocabularyFactory)
