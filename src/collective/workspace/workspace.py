from .events import TeamMemberAddedEvent
from .interfaces import IHasWorkspace
from .interfaces import IWorkspace
from .membership import ITeamMembership
from .membership import TeamMembership
from .pas import add_group
from .pas import get_workspace_groups_plugin
from BTrees.Length import Length
from BTrees.OOBTree import OOBTree
from plone import api
from Products.PluggableAuthService.interfaces.events import IPrincipalDeletedEvent  # noqa: E501
from zope.component import adapter
from zope.container.interfaces import IObjectAddedEvent
from zope.container.interfaces import IObjectRemovedEvent
from zope.event import notify
from zope.lifecycleevent.interfaces import IObjectCopiedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent


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
        for userid in self.context._team.iterkeys():
            yield self[userid]

    def add_to_team(self, userid, groups=None, **kw):
        """
        Makes sure a user is in this workspace's team.

        :param userid: The id of the user to add to this workspace
        :type userid: str
        :param groups: The set of workspace groups to add this user to
        :type groups: set
        :param kw: Pass user and any other attributes that should be set on the
                   team member.
        :type kw: dict
        """
        data = kw.copy()
        data['userid'] = userid
        data['groups'] = groups = set(groups or [])
        members = self.members

        if userid in members:
            membership = self.membership_factory(self, members[userid])
            membership.update(data)
            return membership

        members[userid] = data

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
        return membership

    def remove_from_team(self, userid):
        """
        Remove a user from the workspace

        :param userid: The id of the user to remove from this workspace
        :type userid: str
        """
        membership = self.get(userid)
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
