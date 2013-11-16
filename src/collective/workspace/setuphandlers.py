from Products.PlonePAS.Extensions.Install import activatePluginInterfaces
from Products.PluggableAuthService.interfaces.plugins import IPropertiesPlugin
from zope.component.hooks import getSite


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
