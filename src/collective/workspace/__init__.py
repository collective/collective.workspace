# This needs to go first because it's used from the `pas` module.
from zope.i18nmessageid import MessageFactory
workspaceMessageFactory = MessageFactory('collective.workspace')

from AccessControl.Permissions import add_user_folders  # noqa
from collective.workspace import pas  # noqa
from Products.PluggableAuthService import registerMultiPlugin  # noqa


registerMultiPlugin(pas.WorkspaceGroupManager.meta_type)


def initialize(context):

    context.registerClass(
        pas.WorkspaceGroupManager,
        permission=add_user_folders,
        constructors=(pas.manage_addWorkspaceGroupManagerForm,
                      pas.addWorkspaceGroupManager),
        visibility=None,
    )
