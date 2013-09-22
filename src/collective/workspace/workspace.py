from BTrees.OOBTree import OOBTree
from .events import TeamMemberAddedEvent
from .interfaces import IWorkspace
from .membership import ITeamMembership
from .membership import TeamMembership
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
        u'Admins': ('Contributor', 'Editor', 'Reviewer',
                    'Reader', 'TeamManager',),
    }

    @property
    def members(self):
        """Access the raw team member data."""
        return self.context._team

    def add_to_team(self, **kw):
        """Makes sure a user is in this workspace's team.

        Pass user and any other attributes that should be set on the team member.
        """
        data = kw.copy()
        user = data['user']
        members = self.members
        if user not in self.members:
            if 'groups' not in data:
                data['groups'] = set()
            members[user] = data
            membership = self.membership_factory(self, data)
            membership.handle_added()
            notify(TeamMemberAddedEvent(self.context, membership))
        else:
            membership = self.membership_factory(self, self.members[user])
            membership.update(data)


def handle_creation(object, event):
    """Make sure a workspace's creator is in its Admins team.
    """
    workspace = IWorkspace(object)
    user_id = object.Creator()
    if user_id not in workspace.members:
        workspace.add_to_team(user=user_id, groups=set([u'Admins']))
