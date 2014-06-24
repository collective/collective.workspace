import unittest

from plone import api
from plone.testing import z2
from plone.app.testing import SITE_OWNER_NAME
import transaction

from collective.workspace.testing import \
    COLLECTIVE_WORKSPACE_INTEGRATION_TESTING
from collective.workspace.interfaces import IWorkspace


class TestWorkspace(unittest.TestCase):
    layer = COLLECTIVE_WORKSPACE_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        behaviors = ('collective.workspace.interfaces.IWorkspace', )
        self.portal.portal_types.Folder.behaviors = behaviors
        transaction.commit()

    def test_add_to_team(self):
        z2.login(self.app['acl_users'], SITE_OWNER_NAME)
        user1 = api.user.create(
            email='user1@example.com',
            username='user1',
            password='123'
        )
        workspace = api.content.create(
            container=self.portal,
            type='Workspace',
            id='a-workspace'
        )
        ws = IWorkspace(workspace)
        ws.add_to_team(
            user=user1.getId()
        )
        self.assertIn(user1.getId(), list(ws.members))
