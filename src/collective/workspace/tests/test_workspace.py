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
        z2.login(self.app['acl_users'], SITE_OWNER_NAME)
        self.user1 = api.user.create(
            email='user1@example.com',
            username='user1',
            password='123'
        )
        self.workspace = api.content.create(
            container=self.portal,
            type='Workspace',
            id='a-workspace'
        )
        self.ws = IWorkspace(self.workspace)

    def test_add_to_team(self):
        self.ws.add_to_team(
            user=self.user1.getId()
        )
        self.assertIn(self.user1.getId(), list(self.ws.members))

    def test_remove_from_team(self):
        self.ws.add_to_team(
            user=self.user1.getId()
        )
        self.ws.remove_from_team(
            user=self.user1.getId()
        )
        self.assertNotIn(self.user1.getId(), list(self.ws.members))
