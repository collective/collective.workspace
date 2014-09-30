from Products.CMFCore.utils import getToolByName
from Products.PlonePAS.Extensions.Install import activatePluginInterfaces
from Products.PluggableAuthService.interfaces.plugins import IPropertiesPlugin
from zope.component.hooks import getSite
from .interfaces import IHasWorkspace
from .interfaces import IWorkspace


def setup_pas(context):
    if context.readDataFile('collective.workspace.txt') is None:
        return

    site = getSite()
    if 'workspace_groups' not in site.acl_users:
        site.acl_users.manage_addProduct[
            'collective.workspace'].addWorkspaceGroupManager(
            'workspace_groups', 'collective.workspace Groups',
            )
        activatePluginInterfaces(site, 'workspace_groups')

        # make sure our properties plugin is above mutable_properties
        plugins = list(site.acl_users.plugins._getPlugins(IPropertiesPlugin))
        try:
            target_index = plugins.index('mutable_properties')
        except ValueError:
            target_index = 0
        plugins.remove('workspace_groups')
        plugins.insert(target_index, 'workspace_groups')
        site.acl_users.plugins._plugins[IPropertiesPlugin] = tuple(plugins)


def migrate_groups(context):
    # Remove workspace_groups plugin

    # Store group membership in the normal group tool
    site = getSite()
    catalog = getToolByName(site, 'portal_catalog')
    gtool = getToolByName(site, 'portal_groups')
    for b in catalog.unrestrictedSearchResults(
            object_provides=IHasWorkspace.__identifier__):
        print b.getPath()
        workspace = IWorkspace(b._unrestrictedGetObject())
        for group_name in workspace.available_groups:
            group_id = '{}:{}'.format(group_name.encode('utf8'), b.UID)
            gtool.addGroup(
                id=group_id,
                title='{}: {}'.format(group_name.encode('utf8'), b.Title),
                )
        for m in workspace:
            new_groups = m.groups & set(workspace.available_groups)
            m._update_groups(set(), new_groups)
