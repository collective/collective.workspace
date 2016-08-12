from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite
from .interfaces import IHasWorkspace
from .interfaces import IWorkspace


def migrate_groups(context):
    site = getSite()

    # Remove workspace_groups plugin
    site.acl_users.workspace_groups.manage_activateInterfaces(())
    site.acl_users.manage_delObjects(ids=['workspace_groups'])

    # Store group membership in the normal group tool
    catalog = getToolByName(site, 'portal_catalog')
    gtool = getToolByName(site, 'portal_groups')
    for b in catalog.unrestrictedSearchResults(
            object_provides=IHasWorkspace.__identifier__):
        print b.getPath()
        workspace = IWorkspace(b._unrestrictedGetObject())
        for group_name in set(workspace.available_groups):
            group_id = '{}:{}'.format(group_name.encode('utf8'), b.UID)
            gtool.addGroup(
                id=group_id,
                title='{}: {}'.format(group_name.encode('utf8'), b.Title),
                )
        for m in workspace:
            new_groups = (m.groups | set([u'Members'])) & set(workspace.available_groups)
            m._update_groups(set(), new_groups, add_auto_groups=False)
