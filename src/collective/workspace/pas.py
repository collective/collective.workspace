from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from borg.localrole.interfaces import ILocalRoleProvider
from collective.workspace import workspaceMessageFactory as _
from collective.workspace.interfaces import IWorkspace
from Products.CMFCore.utils import getToolByName
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PlonePAS.plugins.group import GroupManager
from zope.interface import implements


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

    def addGroup(self, group_id, *args, **kw):
        # Make sure we save the group title via a properties plugin
        res = super(WorkspaceGroupManager, self).addGroup(
            group_id, *args, **kw)
        if kw:
            gtool = getToolByName(self, 'portal_groups')
            group = gtool.getGroupById(group_id)
            group.setGroupProperties(kw)
        return res


InitializeClass(WorkspaceGroupManager)


def get_workspace_groups_plugin(context):
    acl_users = getToolByName(context, 'acl_users')
    return acl_users.workspace_groups


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
