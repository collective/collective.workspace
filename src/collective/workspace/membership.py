from collective.workspace.events import TeamMemberModifiedEvent
from collective.workspace.events import TeamMemberRemovedEvent
from collective.workspace.interfaces import IWorkspace
from collective.workspace.vocabs import UsersSource
from copy import deepcopy
from plone.autoform import directives as form
from plone.formwidget.autocomplete import AutocompleteFieldWidget
from plone.supermodel import model
from plone.uuid.interfaces import IUUIDGenerator
from Products.CMFCore.utils import getToolByName
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope import schema
from zope.component import adapter
from zope.component import getUtility
from zope.event import notify
from zope.interface import implementer


class ITeamMembership(model.Schema):
    """Schema for one person's membership in a team."""

    form.widget(user=AutocompleteFieldWidget)
    user = schema.Choice(
        title=u'User',
        source=UsersSource,
    )

    position = schema.TextLine(
        title=u'Position',
        required=False,
    )

    form.widget(groups=CheckBoxFieldWidget)
    groups = schema.Set(
        title=u'Groups',
        required=False,
        value_type=schema.Choice(
            vocabulary='collective.workspace.groups',
        ),
    )


@implementer(ITeamMembership)
class TeamMembership(object):

    __slots__ = ('workspace', '__dict__')
    _schema = ITeamMembership

    def __init__(self, workspace, data):
        self.workspace = workspace
        if 'UID' not in data:
            data['UID'] = getUtility(IUUIDGenerator)()
        self.__dict__ = data

    def __getattr__(self, name):
        field = self.__class__._schema.get(name, None)
        if field is None:
            raise AttributeError(name)
        field = field.bind(self)
        return deepcopy(field.default)

    def _update_groups(self, old_groups, new_groups, add_members=True):
        workspace = self.workspace
        context = workspace.context
        uid = context.UID()
        gtool = getToolByName(context, 'portal_groups')
        if add_members and u'Members' in workspace.available_groups:
            new_groups |= set([u'Members'])
        for group_name in (new_groups - old_groups):
            group_id = '{}:{}'.format(group_name.encode('utf8'), uid)
            try:
                gtool.addPrincipalToGroup(self.user, group_id)
            except KeyError:  # group doesn't exist
                gtool.addGroup(
                    id=group_id,
                    title='{}: {}'.format(group_name.encode('utf8'), context.Title()),
                )
                gtool.addPrincipalToGroup(self.user, group_id)
        for group_name in (old_groups - new_groups):
            group_id = '{}:{}'.format(group_name.encode('utf8'), uid)
            try:
                gtool.removePrincipalFromGroup(self.user, group_id)
            except KeyError:  # group doesn't exist
                pass

    def update(self, data):
        old = self.__dict__.copy()
        user_changed = False
        if 'user' in data and old['user'] != data['user']:
            # User is changing, so remove the old user from groups.
            user_changed = True
            self._update_groups(old['groups'], set())
        self.__dict__.update(data)
        # make sure change is persisted
        # XXX really we should use PersistentDicts
        workspace = self.workspace
        if user_changed:
            # User changed; remove old entry in _team
            del workspace.context._team[old['user']]
            # Add new user to groups
            self._update_groups(set(), self.groups)
        workspace.context._team[self.user] = self.__dict__

        # update counters
        for name, func in workspace.counters:
            # The following is based on Python's ability to treat booleans
            # as integers (1 or 0)...
            # 0 = no change
            # 1 = matches now but didn't before
            # -1 = matched before but doesn't now
            # Then we use that difference to update the count of how many roster members match.
            diff = func(self.__dict__) - func(old)
            if diff:
                workspace.context._counters[name].change(diff)

        if 'groups' in data:
            self._update_groups(old['groups'], data['groups'])

        self.handle_modified(old)
        notify(TeamMemberModifiedEvent(self.workspace.context, self))
        if user_changed:
            workspace.context.reindexObject(idxs=['workspace_members'])

    def handle_added(self):
        pass

    def handle_modified(self, old):
        pass

    def handle_removed(self):
        pass

    def remove_from_team(self):
        workspace = self.workspace
        for name, func in workspace.counters:
            if func(self.__dict__):
                workspace.context._counters[name].change(-1)
        del self.workspace.members[self.user]
        self._update_groups(self.groups, set(), add_members=False)
        self.handle_removed()
        notify(TeamMemberRemovedEvent(self.workspace.context, self))
        self.workspace.context.reindexObject(idxs=['workspace_members'])


@adapter(ITeamMembership)
@implementer(IWorkspace)
def workspace_from_membership(membership):
    return membership.workspace
