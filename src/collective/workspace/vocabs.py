from Acquisition import aq_chain
from collective.workspace import workspaceMessageFactory as _
from collective.workspace.interfaces import IWorkspace
from Products.CMFCore.utils import getToolByName
from z3c.formwidget.query.interfaces import IQuerySource
from zope.component.hooks import getSite
from zope.interface import classProvides
from zope.interface import directlyProvides
from zope.interface import implements
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


def find_workspace(context):
    while hasattr(context, 'context'):
        context = context.context
    for context in aq_chain(context):
        workspace = IWorkspace(context, None)
        if workspace is not None:
            return workspace


def TeamGroupsVocabulary(context):
    workspace = find_workspace(context)
    # Membership in the Members group is implied by
    # inclusion in the roster, so we don't need to show
    # it as an explicit option.
    groups = set(workspace.available_groups.keys()) - set([u'Members'])
    items = []
    for group in groups:
        items.append(SimpleTerm(group, group, _(group)))
    return SimpleVocabulary(items)

directlyProvides(TeamGroupsVocabulary, IVocabularyFactory)


class UsersSource(object):
    """A source for looking up users.

    Unfortunately the one in plone.app.vocabularies is not
    quite workable with z3c.formwidget.query
    """
    implements(IQuerySource)
    classProvides(IContextSourceBinder)

    def __init__(self, context):
        self._context = context
        self._users = getToolByName(getSite(), "acl_users")

    def __contains__(self, value):
        return self._users.getUserById(value, None) and True or False

    def search(self, query):
        users = set()
        for u in self._users.searchUsers(id=query):
            users.add(u['userid'])
        for u in self._users.searchUsers(fullname=query):
            users.add(u['userid'])
        for u in users:
            yield self.getTerm(u)

    def getTerm(self, userid):
        fullname = userid
        user = self._users.getUserById(userid, None)
        if user:
            fullname = user.getProperty('fullname', None) or userid
        return SimpleTerm(userid, userid, fullname)
    getTermByToken = getTerm

    def __iter__(self):
        for item in self._users.searchUsers():
            yield self.getTerm(item['userid'])

    def __len__(self):
        return len(self._users.searchUsers())
