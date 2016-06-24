from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS.Cache import Cacheable
from Products.CMFCore.utils import getToolByName
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PlonePAS.interfaces.group import IGroupIntrospection
from Products.PluggableAuthService.interfaces.plugins \
    import IGroupEnumerationPlugin
from Products.PluggableAuthService.interfaces.plugins \
    import IGroupsPlugin
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

    implements(
        IGroupsPlugin,
        IGroupEnumerationPlugin,
        IGroupIntrospection,
        IPropertiesPlugin,
    )

    def __init__(self, id, title=None):
        self._id = self.id = id
        self.title = title

    def get_cache(self):
        ''' Get the request cache more reliably

        Infact in the __init__ is not setting properly self.REQUEST.
        In case this happen fallback to use
        `zope.globalrequest.getRequest` method.

        If this also fails, just return a dict,
        which is good enough for our use case.
        '''
        try:
            request = self.REQUEST
        except AttributeError:
            request = getRequest()
        return IAnnotations(request, {})

    def _iterWorkspaces(self, userid=None):
        cache = self.get_cache()
        workspaces = cache.get(('workspaces', userid))
        if workspaces is None:
            catalog = getToolByName(self, 'portal_catalog')
            query = {'object_provides': WORKSPACE_INTERFACE}
            if userid:
                query['workspace_members'] = userid
            workspaces = [
                IWorkspace(b._unrestrictedGetObject())
                for b in catalog.unrestrictedSearchResults(query)
            ]
            cache[('workspaces', userid)] = workspaces

        return iter(workspaces)

    def _getWorkspace(self, uid):
        catalog = getToolByName(self, 'portal_catalog')
        res = catalog.unrestrictedSearchResults(
            object_provides=WORKSPACE_INTERFACE,
            UID=uid
        )
        if not res:
            return

        return IWorkspace(res[0]._unrestrictedGetObject())

    #
    #   IGroupsPlugin implementation
    #
    def getGroupsForPrincipal(self, principal, request=None):
        # Skip principals that look like workspace groups,
        # because we're not going to find them as workspace members
        user_id = principal.getId()
        if ':' in user_id:
            return ()

        cache = self.get_cache()
        groups = cache.get(('workspace_groups', user_id))
        if groups is not None:
            return groups

        # For each workspace:
        #   If workspace has this user:
        #      Return that user's workspace groups
        groups = []
        for workspace in self._iterWorkspaces(user_id):
            member_data = workspace.members.get(user_id)
            if member_data is not None:
                member_groups = set(member_data['groups'])
                # Membership in the Members group is implied, but only for
                # members who are not Guests
                if "Guests" not in member_data['groups']:
                    member_groups = member_groups | set([u'Members'])
                groups.extend([
                    '%s:%s' % (group_name, workspace.context.UID())
                    for group_name in member_groups
                ])
        res = tuple(groups)
        cache[('workspace_groups', user_id)] = res
        return res

    security.declarePrivate('getGroupsForPrincipal')

    #
    #   IGroupEnumerationPlugin implementation
    #
    def enumerateGroups(self,
                        id=None,
                        title=None,
                        exact_match=False,
                        sort_by=None,
                        max_results=None,
                        **kw
                        ):
        group_info = []
        plugin_id = self.getId()

        if id and isinstance(id, str):
            id = [id]

        if isinstance(title, str):
            title = [title]

        catalog = getToolByName(self, 'portal_catalog')
        query = {
            'object_provides': WORKSPACE_INTERFACE,
            'sort_on': 'sortable_title',
        }

        if id:
            target_group_names = set()
            uid_query = list()
            for one_id in id:
                target_group_name, workspace_uid = one_id.split(':')
                target_group_names.add(target_group_name)
                uid_query.append(workspace_uid)
            query['UID'] = uid_query

        elif title:
            query['Title'] = exact_match and title or [
                '%s*' % t for t in title if t]

        i = 0
        for brain in catalog.unrestrictedSearchResults(query):
            obj = brain._unrestrictedGetObject()
            workspace = IWorkspace(obj)
            for group_name in workspace.available_groups:
                group_name = group_name.encode('utf8')

                if id and group_name not in target_group_names:
                    continue
                if (title and exact_match and
                        not any(t == brain.Title for t in title)):
                    continue
                if (title and not exact_match and not
                        any(t.lower() in brain.Title.lower() for t in title)):
                    continue

                i += 1
                if max_results is not None and i >= max_results:
                    break

                workspace_url = obj.absolute_url() + '/team-roster'
                info = {
                    'id': group_name + ':' + brain.UID,
                    'title': group_name + ': ' + brain.Title,
                    'pluginid': plugin_id,
                    'properties_url': workspace_url,
                    'members_url': workspace_url,
                }
                group_info.append(info)
        return tuple(group_info)
    security.declarePrivate('enumerateGroups')

    #
    #   IGroupIntrospectionPlugin implementation
    #

    def getGroupById(self, group_id, default=None):
        if not group_id:
            return default
        if ':' not in group_id:
            return default
        pas = self._getPAS()
        plugins = pas._getOb('plugins')
        groups_plugin = pas.source_groups
        return groups_plugin._findGroup(plugins, group_id)
    security.declarePrivate('getGroupById')

    def getGroups(self):
        pas = self._getPAS()
        plugins = pas._getOb('plugins')
        groups_plugin = pas.source_groups

        groups = []
        for workspace in self._iterWorkspaces():
            for group_name in workspace.available_groups:
                group_id = (
                    group_name.encode('utf8') + ':' + workspace.context.UID())
                groups.append(groups_plugin._findGroup(plugins, group_id))
        return groups
    security.declarePrivate('getGroups')

    def getGroupIds(self):
        group_ids = []
        for workspace in self._iterWorkspaces():
            for group_name in workspace.available_groups:
                group_ids.append(
                    '%s:%s' % (
                        group_name.encode('utf8'), workspace.context.UID()))
        return group_ids
    security.declarePrivate('getGroupIds')

    def getGroupMembers(self, group_id):
        if ':' not in group_id:
            return ()

        group_name, workspace_uid = group_id.split(':')
        if isinstance(group_name, str):
            group_name = group_name.decode('utf8')
        workspace = self._getWorkspace(workspace_uid)
        if workspace is not None:
            return tuple(
                u for u, data in workspace.members.items()
                if group_name in data['groups']
                # Membership in the Members group is implied
                or group_name == u'Members'
            )
        return ()
    security.declarePrivate('getGroupMembers')

    def getPropertiesForUser(self, user, request=None):
        group_id = user.getId()
        if ':' not in group_id:
            return {}

        group_name, workspace_uid = user.getId().split(':')
        workspace = self._getWorkspace(workspace_uid)
        if workspace is not None:
            if group_name in workspace.available_groups:
                workspace_title = workspace.context.Title().decode('utf8')
                return {'title': group_name + ': ' + workspace_title}

        return {}
    security.declarePrivate('getPropertiesForUser')


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
