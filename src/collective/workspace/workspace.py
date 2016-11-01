from BTrees.Length import Length
from BTrees.OOBTree import OOBTree
from DateTime import DateTime
from plone.uuid.interfaces import IUUIDGenerator
from Products.PluggableAuthService.interfaces.events import \
    IPrincipalDeletedEvent
from .events import TeamMemberAddedEvent
from .interfaces import IHasWorkspace
from .interfaces import IWorkspace
from .membership import ITeamMembership
from .membership import TeamMembership
from .pas import get_workspace_groups_plugin
from .pas import add_group
from plone import api
from zope.component import adapter
from zope.component import getUtility
from zope.container.interfaces import IObjectAddedEvent
from zope.container.interfaces import IObjectRemovedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.lifecycleevent.interfaces import IObjectCopiedEvent
from zope.event import notify


class Workspace(object):
    """Provides access to team workspace functionality.

    This is registered as a behavior providing the IWorkspace interface.
    """

    def __init__(self, context):
        self.context = context

        # create a BTree to store team member data
        if not hasattr(self.context, '_team'):
            self.context._team = OOBTree()

        if not hasattr(self.context, '_counters'):
            self._recount()

    def _recount(self):
        counters = {}
        for name, func in self.counters:
            counters[name] = Length()
        for m in self.context._team.itervalues():
            for name, func in self.counters:
                if func(m):
                    counters[name].change(1)
        self.context._counters = counters

    @property
    def membership_schema(self):
        """Returns the schema to be used for editing team memberships.
        """
        return ITeamMembership

    membership_factory = TeamMembership

    # A list of groups to which team members can be assigned.
    # Maps group name -> roles
    available_groups = {
        u'Members': ('Contributor', 'Reader', 'TeamMember'),
        u'Guests': ('TeamGuest', ),
        u'Admins': ('Contributor', 'Editor', 'Reviewer',
                    'Reader', 'TeamManager',),
    }

    # Add everyone on the roster to the Members group
    auto_groups = {
        u'Members': lambda x: 'Guests' not in x.groups,
    }

    counters = (
        ('members', lambda x: True),
    )

    @property
    def members(self):
        """Access the raw team member data."""
        return self.context._team

    def __getitem__(self, name):
        memberdata = self.context._team[name]
        return self.membership_factory(self, memberdata)

    def get(self, name, default=None):
        try:
            return self[name]
        except KeyError:
            return default

    def __iter__(self):
        for key in self.context._team.iterkeys():
            yield self[key]

    def add_to_team(self, user, groups=None, **kw):
        """
        Makes sure a user is in this workspace's team.

        :param user: The id of the user to add to this workspace
        :type user: str
        :param groups: The set of workspace groups to add this user to
        :type groups: set
        :param kw: Pass user and any other attributes that should be set on the
                   team member.
        :type kw: dict
        """
        # TODO: user argument should be renamed to userid for clarity
        #       however doing so now would break backwards compatibility
        data = kw.copy()
        data['user'] = user
        if groups is not None:
            data['groups'] = groups = set(groups)
        members = self.members
        if not user or user not in members:
            data['UID'] = uid = getUtility(IUUIDGenerator)()
            key = user or uid
            data['_mtime'] = DateTime()
            if groups is None:
                data['groups'] = groups = set()
            members[key] = data
            for name, func in self.counters:
                if func(data):
                    if name not in self.context._counters:
                        self.context._counters[name] = Length()
                    self.context._counters[name].change(1)
            membership = self.membership_factory(self, data)
            membership.handle_added()
            membership._update_groups(set(), groups)
            notify(TeamMemberAddedEvent(self.context, membership))
            self.context.reindexObject(
                idxs=['workspace_members', 'workspace_leaders']
            )
        else:
            membership = self.membership_factory(self, self.members[user])
            membership.update(data)
        return membership

    def remove_from_team(self, user):
        """
        Remove a user from the workspace

        :param user: The id of the user to remove from this workspace
        :type user: str
        """
        # TODO: user argument should be renamed to key for clarity
        #       however doing so now would break backwards compatibility
        key = user
        membership = self.get(key)
        if membership is not None:
            membership.remove_from_team()
        return membership


@adapter(IHasWorkspace, IObjectAddedEvent)
def handle_workspace_added(context, event):
    workspace = IWorkspace(context)
    for group_name in workspace.available_groups:
        group_id = '{}:{}'.format(group_name.encode('utf8'), context.UID())
        title = '{}: {}'.format(group_name.encode('utf8'), context.Title())
        add_group(group_id, title)


@adapter(IHasWorkspace, IObjectModifiedEvent)
def handle_workspace_modified(context, event):
    workspace = IWorkspace(context)
    gtool = api.portal.get_tool('portal_groups')
    for group_name in workspace.available_groups:
        group_id = '{}:{}'.format(group_name.encode('utf8'), context.UID())
        group_title = '{}: {}'.format(
            group_name.encode('utf8'), context.Title())
        group = gtool.getGroupById(group_id)
        if group is not None:
            group.setProperties(title=group_title)


@adapter(IHasWorkspace, IObjectRemovedEvent)
def handle_workspace_removed(context, event):
    workspace = IWorkspace(context)
    workspace_groups = get_workspace_groups_plugin()
    for group_name in workspace.available_groups:
        group_id = '{}:{}'.format(group_name.encode('utf8'), context.UID())
        try:
            workspace_groups.removeGroup(group_id)
        except KeyError:  # group already doesn't exist
            pass


@adapter(IHasWorkspace, IObjectCopiedEvent)
def handle_workspace_copied(context, event):
    if hasattr(context, '_team'):
        del context._team
    if hasattr(context, '_counters'):
        del context._counters


@adapter(IPrincipalDeletedEvent)
def handle_principal_deleted(event):
    """When a user is deleted, remove it from all workspaces."""
    principal = event.principal
    catalog = api.portal.get_tool('portal_catalog')
    for b in catalog.unrestrictedSearchResults(workspace_members=principal):
        workspace = IWorkspace(b._unrestrictedGetObject(), None)
        if workspace is not None:
            membership = workspace.get(principal)
            if membership is not None:
                membership.remove_from_team()
