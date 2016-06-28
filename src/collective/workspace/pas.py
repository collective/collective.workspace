from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from borg.localrole.interfaces import ILocalRoleProvider
from collective.workspace import workspaceMessageFactory as _
from collective.workspace.interfaces import IWorkspace
from Products.CMFCore.utils import getToolByName
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PlonePAS.plugins.group import GroupManager
from zope.interface import implements


PLUGIN_ID = 'workspace_groups'


manage_addWorkspaceGroupManagerForm = PageTemplateFile(
    'templates/WorkspaceGroupManagerForm',
    globals(),
    __name__='manage_addWorkspaceGroupManagerForm'
)


def addWorkspaceGroupManager(dispatcher, id, title=None, REQUEST=None):
    """ Add a WorkspaceGroupManager to a Pluggable Auth Service. """

    pmm = WorkspaceGroupManager(id, title)
    dispatcher._setObject(pmm.getId(), pmm)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(
            '%s/manage_workspace?manage_tabs_message='
            'WorkspaceGroupManager+added.'
            % dispatcher.absolute_url()
        )


class WorkspaceGroupManager(GroupManager):
    """PAS plugin to store groups created from the team rosters.

    We use a separate plugin from the standard Plone group plugin
    so that enumeration can optionally be disabled to prevent
    workspace groups from showing up in sharing and the groups
    control panel.
    """

    meta_type = 'collective.workspace Group Manager'

    security = ClassSecurityInfo()

    # disable editing workspace groups via control panel

    def allowDeletePrincipal(self, principal_id):
        return False

    def allowGroupAdd(self, user_id, group_id):
        return False

    def allowGroupRemove(self, user_id, group_id):
        return False

InitializeClass(WorkspaceGroupManager)


def get_workspace_groups_plugin(context):
    acl_users = getToolByName(context, 'acl_users')
    return getattr(acl_users, PLUGIN_ID)


def add_group(context, group_id, title):
    workspace_groups = get_workspace_groups_plugin(context)
    if group_id not in workspace_groups._groups:
        workspace_groups.addGroup(group_id)
    gtool = getToolByName(context, 'portal_groups')
    group = gtool.getGroupById(group_id)
    group.setGroupProperties({'title': title})


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
