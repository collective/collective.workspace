import unittest

from plone import api
from plone.testing import z2
from plone.app.testing import SITE_OWNER_NAME

from collective.workspace.pas import WorkspaceGroupManager
from collective.workspace.testing import \
    COLLECTIVE_WORKSPACE_INTEGRATION_TESTING
from collective.workspace.interfaces import IWorkspace
from zope.annotation import IAnnotations
from zope.annotation.attribute import AttributeAnnotations
from zope.component.interfaces import ObjectEvent
from zope.event import notify


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

    def test_cache_purging_on_event(self):
        ''' Test we can purge the cache
        '''
        # Reading permissions on a workspace taints the annotations
        api.user.get_permissions(user=self.user1, obj=self.ws)
        IAnnotations(self.request)
        self.assertIn(
            ('workspaces', 'user1'),
            IAnnotations(self.request),
        )
        # Notifying an event on the workspace cleans up the annotations
        notify(ObjectEvent(self.workspace))
        self.assertNotIn(
            ('workspaces', 'user1'),
            IAnnotations(self.request),
        )

    def test_add_to_team(self):
        self.ws.add_to_team(
            user=self.user1.getId()
        )
        self.assertIn(self.user1.getId(), list(self.ws.members))

    def test_local_role_team_member(self):
        self.ws.add_to_team(
            user=self.user1.getId()
        )
        pmt = api.portal.get_tool('portal_membership')
        member = pmt.getMemberById(self.user1.getId())
        roles = member.getRolesInContext(self.workspace)
        self.assertIn('TeamMember', roles)

    def test_remove_from_team(self):
        self.ws.add_to_team(
            user=self.user1.getId()
        )
        self.ws.remove_from_team(
            user=self.user1.getId()
        )
        self.assertNotIn(self.user1.getId(), list(self.ws.members))

    def test_add_guest_to_team(self):
        self.ws.add_to_team(
            user=self.user1.getId(), groups=['Guests']
        )
        self.assertIn(self.user1.getId(), list(self.ws.members))

    def test_guest_has_no_team_member_role(self):
        self.ws.add_to_team(
            user=self.user1.getId(), groups=['Guests']
        )
        pmt = api.portal.get_tool('portal_membership')
        member = pmt.getMemberById(self.user1.getId())
        roles = member.getRolesInContext(self.workspace)
        self.assertIn('TeamGuest', roles)
        self.assertNotIn('TeamMember', roles)

    def test_cache_fallback(self):
        ''' Check if we can have a cache even if the plugin is not properly
        initialized
        '''
        # Ususally the plugin is working fine
        workspace_groups = self.portal.acl_users.workspace_groups
        self.assertIsInstance(
            IAnnotations(workspace_groups.REQUEST),
            AttributeAnnotations
        )
        self.assertIsInstance(
            workspace_groups.get_cache(),
            AttributeAnnotations
        )

        # but we can have border line cases where it is going to fail
        wgm = WorkspaceGroupManager('test', title='Test')
        self.assertEqual(
            wgm.REQUEST,
            '<Special Object Used to Force Acquisition>'
        )
        self.assertIsInstance(
            wgm.get_cache(),
            dict
        )
