from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS.Cache import Cacheable
from Products.CMFCore.utils import getToolByName
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PlonePAS.interfaces.group import IGroupIntrospection
from Products.PluggableAuthService.interfaces.plugins \
    import IGroupEnumerationPlugin
from Products.PluggableAuthService.interfaces.plugins \
    import IPropertiesPlugin
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from borg.localrole.interfaces import ILocalRoleProvider
from collective.workspace import workspaceMessageFactory as _
from collective.workspace.interfaces import IWorkspace
from zope.annotation.interfaces import IAnnotations
from zope.globalrequest import getRequest
from zope.interface import implements


manage_addWorkspaceGroupManagerForm = PageTemplateFile(
    'templates/WorkspaceGroupManagerForm',
    globals(),
    __name__='manage_addWorkspaceGroupManagerForm'
)


def purge_workspace_pas_cache():
    ''' Completely removes workspace pas plugin cache from the request
    '''
    request = getRequest()
    if not request:
        return

    annotations = IAnnotations(request)
    keys_to_remove = [
        key for key in annotations.keys()
        if (
            key and
            isinstance(key, tuple) and
            key[0] in ('workspaces', 'workspace_groups')
        )
    ]
    map(annotations.pop, keys_to_remove)


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


WORKSPACE_INTERFACE = 'collective.workspace.interfaces.IHasWorkspace'


class WorkspaceGroupManager(BasePlugin, Cacheable):
    """PAS plugin to dynamically create groups from the team rosters."""

    meta_type = 'collective.workspace Group Manager'

    security = ClassSecurityInfo()

    def __init__(self, id, title=None):
        self._id = self.id = id
        self.title = title

InitializeClass(WorkspaceGroupManager)


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
