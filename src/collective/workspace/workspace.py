from BTrees.OOBTree import OOBTree
from .interfaces import IWorkspace
from .membership import ITeamMembership


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


def handle_creation(object, event):
    """Make sure a workspace's creator is in its Admins team.
    """
    workspace = IWorkspace(object)
    user_id = object.Creator()
    if user_id not in workspace.members:
        workspace.members[user_id] = {'user': user_id, 'groups': set([u'Admins'])}
