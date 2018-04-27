# coding=utf-8
from collective.workspace.interfaces import IWorkspace
from collective.workspace.testing import COLLECTIVE_WORKSPACE_INTEGRATION_TESTING  # noqa: E501
from plone import api
from plone.app.testing import SITE_OWNER_NAME
from plone.testing import z2

import unittest


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

    def _get_roles_in_workspace(self):
        pmt = api.portal.get_tool('portal_membership')
        member = pmt.getMemberById(self.user1.getId())
        return member.getRolesInContext(self.workspace)

    def test_adding_workspace_creates_groups(self):
        group = self.portal.portal_groups.getGroupById(
            'Admins:' + self.workspace.UID())
        self.assertIsNotNone(group)

    def test_renaming_workspace_updates_group_titles(self):
        self.workspace.setTitle('new title')
        from zope.lifecycleevent import modified
        modified(self.workspace)
        group = self.portal.portal_groups.getGroupById(
            'Admins:' + self.workspace.UID())
        self.assertEqual(group.getProperty('title'), 'Admins: new title')

    def test_removing_workspace_removes_groups(self):
        self.portal.manage_delObjects(['a-workspace'])
        group = self.portal.portal_groups.getGroupById(
            'Admins:' + self.workspace.UID())
        self.assertIsNone(group)

    def test_add_to_team(self):
        self.ws.add_to_team(
            user=self.user1.getId()
        )
        self.assertIn(self.user1.getId(), list(self.ws.members))

    def test_adding_team_member_updates_groups(self):
        self.ws.add_to_team(
            user=self.user1.getId(),
            groups=(u'Admins',),
            )
        self.assertIn(
            self.user1.getId(),
            self.portal.portal_groups.getGroupMembers(
                'Members:' + self.workspace.UID()),
        )
        self.assertIn(
            self.user1.getId(),
            self.portal.portal_groups.getGroupMembers(
                'Admins:' + self.workspace.UID()),
        )

    def test_updating_team_member_updates_groups(self):
        self.ws.add_to_team(
            user=self.user1.getId()
        )
        self.ws[self.user1.getId()].update({'groups': set([u'Admins'])})
        self.assertIn(
            self.user1.getId(),
            self.portal.portal_groups.getGroupMembers(
                'Members:' + self.workspace.UID()),
        )
        self.assertIn(
            self.user1.getId(),
            self.portal.portal_groups.getGroupMembers(
                'Admins:' + self.workspace.UID()),
        )

    def test_direct_set_of_membership_property_is_blocked(self):
        self.ws.add_to_team(
            user=self.user1.getId()
        )
        try:
            self.ws[self.user1.getId()].position = u'Tester'
        except Exception as e:
            self.assertEqual(
                str(e),
                'Setting membership properties directly is not supported. '
                'Use the `update` method instead.'
            )
        else:
            self.fail('Expected exception')

    def test_local_role_team_member(self):
        self.ws.add_to_team(
            user=self.user1.getId()
        )
        self.assertIn('TeamMember', self._get_roles_in_workspace())

    def test_remove_from_team(self):
        self.ws.add_to_team(
            user=self.user1.getId()
        )
        self.ws.remove_from_team(
            user=self.user1.getId()
        )
        self.assertNotIn(self.user1.getId(), list(self.ws.members))

    def test_removing_team_member_updates_groups(self):
        self.ws.add_to_team(
            user=self.user1.getId(),
            groups=(u'Admins',),
        )
        self.ws.remove_from_team(
            user=self.user1.getId()
        )
        self.assertNotIn(
            self.user1.getId(),
            self.portal.portal_groups.getGroupMembers(
                'Members:' + self.workspace.UID()),
        )
        self.assertNotIn(
            self.user1.getId(),
            self.portal.portal_groups.getGroupMembers(
                'Admins:' + self.workspace.UID()),
        )

    def test_reparent_team_member(self):
        self.ws.add_to_team(
            user=self.user1.getId(),
            groups=(u'Admins',),
            )
        user2 = api.user.create(
            email='user2@example.com',
            username='user2',
            password='123'
        )
        self.ws[self.user1.getId()].update({'user': user2.getId()})
        self.assertNotIn(self.user1.getId(), self.workspace._team)
        self.assertIn(user2.getId(), self.workspace._team)
        self.assertEqual(self.ws[user2.getId()].user, user2.getId())
        self.assertNotIn(
            self.user1.getId(),
            self.portal.portal_groups.getGroupMembers(
                'Admins:' + self.workspace.UID()),
        )
        self.assertIn(
            user2.getId(),
            self.portal.portal_groups.getGroupMembers(
                'Admins:' + self.workspace.UID()),
        )

    def test_removing_user_removes_workspace_memberships(self):
        userid = self.user1.getId()
        self.ws.add_to_team(user=userid)
        self.assertIn(userid, self.ws.members)
        api.user.delete(userid)
        self.assertNotIn(userid, self.ws.members)
        self.assertNotIn(
            userid,
            self.portal.portal_groups.getGroupMembers(
                'Members:' + self.workspace.UID()),
        )

    def test_copying_workspace_clears_roster(self):
        cookie = self.portal.manage_copyObjects(ids=('a-workspace',))
        self.portal.manage_pasteObjects(cookie)

        self.assertTrue('copy_of_a-workspace' in self.portal)
        workspace = self.portal['copy_of_a-workspace']
        self.assertEqual(len(workspace._team), 0)
        self.assertEqual(workspace._counters['members'](), 0)

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

    def test_creating_and_removing_plone_groups_is_possible(self):
        test_group_id = 'My workspace testers'
        self.assertIsNone(api.group.get(test_group_id))
        api.group.create(test_group_id)
        group = api.group.get(test_group_id)
        self.assertEquals(group.getId(), test_group_id)
        api.group.delete(test_group_id)
        self.assertIsNone(api.group.get(test_group_id))

    def test_update_membership_groups(self):
        ''' Test that calling _update_groups will always add
        the Members group, unless the user is also in the Guests group
        '''
        self.assertNotIn('TeamMember', self._get_roles_in_workspace())

        # Adding the user to the workspace will grant the TeamMember role
        membership = self.ws.add_to_team(user=self.user1.getId())
        self.assertIn('TeamMember', self._get_roles_in_workspace())

        # groups should be untouched
        old = set()
        new = set()
        membership._update_groups(old, new)
        self.assertIn('TeamMember', self._get_roles_in_workspace())

        # groups should be untouched because user is already a member
        old = set()
        new = set(['Members'])
        membership._update_groups(old, new)
        self.assertIn('TeamMember', self._get_roles_in_workspace())

        # Removing the automatic group will not actually remove it
        # because it is an automatic group
        old = set(['Members'])
        new = set()
        membership._update_groups(old, new)
        self.assertIn('TeamMember', self._get_roles_in_workspace())

        # Removing the automatic group will have no effect
        old = set(['Members'])
        new = set()
        membership._update_groups(old, new)
        self.assertIn('TeamMember', self._get_roles_in_workspace())

        # Adding the user to the Guests group will remove it from the Members
        # because the condition will not be satisifed
        old = set()
        new = set(['Guests'])
        membership._update_groups(old, new)
        self.assertIn('TeamGuest', self._get_roles_in_workspace())
        self.assertNotIn('TeamMember', self._get_roles_in_workspace())

    def test_membership_remove_all_groups(self):
        ''' Test that calling _remove_all_groups does so
        '''
        self.assertNotIn('TeamMember', self._get_roles_in_workspace())

        # Adding the user to the workspace will grant the TeamMember role
        membership = self.ws.add_to_team(user=self.user1.getId())
        self.assertIn('TeamMember', self._get_roles_in_workspace())

        # groups should be removed
        membership._remove_all_groups()
        self.assertNotIn('TeamMember', self._get_roles_in_workspace())
