from Products.PlonePAS.setuphandlers import activatePluginInterfaces
from zope.component.hooks import getSite

import logging

logger = logging.getLogger("collective.workspace")


def setup_pas(context):
    if context.readDataFile("collective.workspace.txt") is None:
        return

    site = getSite()
    if "workspace_groups" not in site.acl_users:
        site.acl_users.manage_addProduct[
            "collective.workspace"
        ].addWorkspaceGroupManager(
            "workspace_groups",
            "collective.workspace Groups",
        )
        activatePluginInterfaces(site, "workspace_groups")
