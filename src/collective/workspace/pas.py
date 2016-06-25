from borg.localrole.interfaces import ILocalRoleProvider
from collective.workspace import workspaceMessageFactory as _
from collective.workspace.interfaces import IWorkspace
from zope.interface import implements


class WorkspaceRoles(object):
    """Automatically assign local roles to workspace groups.
    """
    implements(ILocalRoleProvider)

    def __init__(self, context):
        self.workspace = IWorkspace(context)
        self.uid = context.UID()

    def getAllRoles(self):
        for group_name, roles in self.workspace.available_groups.items():
            group_id = group_name.encode('utf8') + ':' + self.uid
            yield group_id, roles

    def getRoles(self, user_id):
        for group_id, group_roles in self.getAllRoles():
            if user_id == group_id:
                return group_roles
        return ()


# Make the MemberAdmin role show up on the Sharing tab
class TeamManagerRoleDelegation(object):
    title = _(u"Can edit roster")
    required_permission = "collective.workspace: Manage roster"
