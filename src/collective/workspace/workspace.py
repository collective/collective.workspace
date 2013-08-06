from BTrees.OOBTree import OOBTree
from .events import TeamMemberModifiedEvent
from .interfaces import IWorkspace
from .membership import ITeamMembership
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

    @property
    def available_groups(self):
        """Lists groups to which team members can be assigned.

        Returns a mapping of group name -> roles
        """
        return {
            u'Members': ('Contributor', 'Reader'),
            u'Admins': ('Contributor', 'Editor', 'Reviewer',
                        'Reader', 'TeamManager',),
        }

    @property
    def members(self):
        """Access the raw team member data."""
        return self.context._team

    def add_to_team(self, user_id, default_position=None, **kw):
        """Makes sure a user is in this workspace's team.

        If the user was not in the team before, the position will
        be set to default_position.

        Extra keyword arguments will be set on the team member.
        """
        members = self.members
        if user_id not in members:
            members[user_id] = {
                'user': user_id,
                'position': None,
                'groups': set(),
            }
        members[user_id].update(kw)
        notify(TeamMemberModifiedEvent(self.context, members[user_id]))


def handle_creation(object, event):
    """Make sure a workspace's creator is in its Admins team.
    """
    workspace = IWorkspace(object)
    user_id = object.Creator()
    if user_id not in workspace.members:
        workspace.members[user_id] = {'user': user_id, 'groups': set([u'Admins'])}
