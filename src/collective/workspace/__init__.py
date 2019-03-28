# -*- coding: utf-8 -*-
from AccessControl.Permissions import add_user_folders
from collective.workspace import pas
from Products.PluggableAuthService import registerMultiPlugin
from zope.i18nmessageid import MessageFactory

workspaceMessageFactory = MessageFactory('collective.workspace')


registerMultiPlugin(pas.WorkspaceGroupManager.meta_type)


def initialize(context):

    context.registerClass(
        pas.WorkspaceGroupManager,
        permission=add_user_folders,
        constructors=(pas.manage_addWorkspaceGroupManagerForm,
                      pas.addWorkspaceGroupManager),
        visibility=None,
    )
