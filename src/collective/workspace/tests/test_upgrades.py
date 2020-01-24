# coding=utf-8
from collective.workspace.interfaces import IWorkspace
from collective.workspace.testing import COLLECTIVE_WORKSPACE_INTEGRATION_TESTING
from plone import api
from Products.GenericSetup.upgrade import listUpgradeSteps

import unittest


class TestWorkspace(unittest.TestCase):
    layer = COLLECTIVE_WORKSPACE_INTEGRATION_TESTING

    def test_to0003(self):
        pt = api.portal.get_tool("portal_types")
        pt["Workspace"].behaviors = ("foo", IWorkspace.__identifier__, "bar")
        ps = api.portal.get_tool("portal_setup")
        upgrade_steps = listUpgradeSteps(ps, "collective.workspace:default", "0002")
        for upgrade_step in upgrade_steps:
            upgrade_step["step"].doStep(ps)
        self.assertTupleEqual(
            pt["Workspace"].behaviors,
            ("foo", "collective.workspace.team_workspace", "bar"),
        )
