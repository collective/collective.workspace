# coding=utf-8
from .interfaces import IHasWorkspace
from .interfaces import IWorkspace
from .pas import add_group
from .pas import get_workspace_groups_plugin
from plone import api
from plone.dexterity.interfaces import IDexterityFTI
from Products.CMFPlone.utils import safe_encode
from Products.PlonePAS.setuphandlers import activatePluginInterfaces
from zope.component.hooks import getSite

import logging
import six


try:
    from Products.CMFPlone.utils import safe_nativestring
except ImportError:
    from collective.workspace._compat import safe_nativestring


logger = logging.getLogger("collective.workspace")


def setup_pas(context):
    if context.readDataFile("collective.workspace.txt") is None:
        return

    site = getSite()
    if "workspace_groups" not in site.acl_users:
        site.acl_users.manage_addProduct[
            "collective.workspace"
        ].addWorkspaceGroupManager(
            "workspace_groups", "collective.workspace Groups",
        )
        activatePluginInterfaces(site, "workspace_groups")


def migrate_groups(context):
    workspace_groups = get_workspace_groups_plugin()
    if hasattr(workspace_groups, "_groups"):
        # Already migrated
        return

    # Reinitialize groups plugin because its base class changed
    workspace_groups.__init__(workspace_groups.id, workspace_groups.title)

    # Store existing workspace group membership in workspace_groups
    catalog = api.portal.get_tool("portal_catalog")
    for b in catalog.unrestrictedSearchResults(
        object_provides=IHasWorkspace.__identifier__
    ):
        logger.info("Migrating workspace groups for {}".format(b.getPath()))
        workspace = IWorkspace(b._unrestrictedGetObject())
        for group_name in set(workspace.available_groups):
            group_name = safe_nativestring(group_name)
            group_id = "{}:{}".format(group_name, b.UID)
            title = "{}: {}".format(group_name, b.Title)
            add_group(group_id, title)
        for m in workspace:
            new_groups = m.groups & set(workspace.available_groups)
            m._update_groups(set(), new_groups)


def move_dotted_to_named_behaviors(context):
    """ https://github.com/plone/plone.app.upgrade/blob/master/plone/app/upgrade/v52/alphas.py#L58  # noqa: E501
    """
    mapping = {IWorkspace.__identifier__: "collective.workspace.team_workspace"}

    ptt = api.portal.get_tool("portal_types")
    ftis = (fti for fti in ptt.objectValues() if IDexterityFTI.providedBy(fti))
    for fti in ftis:
        behaviors = []
        change_needed = False
        for behavior in fti.behaviors:
            if behavior in mapping:
                behavior = mapping[behavior]
                change_needed = True
            behaviors.append(behavior)
        if change_needed:
            fti.behaviors = tuple(behaviors)

    logger.info("Done moving dotted to named behaviors.")


def fix_workspace_members(context):
    """ This makes sense only on Python2 because on Python3 the index keys
    will already be str instances in any case
    """
    if not six.PY2:
        return
    pc = api.portal.get_tool("portal_catalog")
    index = pc._catalog.indexes.get("workspace_members")
    if not index:
        return
    keys_to_fix = [key for key in index._index if isinstance(key, six.text_type)]
    for key in keys_to_fix:
        index._index[safe_encode(key)] = index._index.pop(key)
