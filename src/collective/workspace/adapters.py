# coding=utf-8
from collective.workspace.interfaces import IHasWorkspace
from plone import api
from plone.app.dexterity.permissions import DXFieldPermissionChecker
from zope.component import adapter


@adapter(IHasWorkspace)
class WorkspaceFieldPermissionChecker(DXFieldPermissionChecker):
    def validate(self, field_name, vocabulary_name=None):
        """ Override the permission checker to allow querying the users
        vocabulary even if there is no user field in this context
        """
        if (
            field_name == "user"
            and vocabulary_name == "plone.app.vocabularies.Users"
            and api.user.has_permission(
                "collective.workspace: Manage roster", obj=self.context
            )
        ):
            return True
        return super(WorkspaceFieldPermissionChecker, self).validate(
            field_name, vocabulary_name
        )
