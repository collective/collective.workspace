# coding=utf-8
from collective.workspace.testing import COLLECTIVE_WORKSPACE_INTEGRATION_TESTING
from Products.CMFPlone.utils import get_installer

import unittest


class TestExample(unittest.TestCase):

    layer = COLLECTIVE_WORKSPACE_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.installer = get_installer(self.portal)

    def test_product_is_installed(self):
        """ Validate that our products GS profile has been run and the product
            installed
        """
        pid = "collective.workspace"
        is_installed = self.installer.is_product_installed(pid)
        self.assertTrue(is_installed)
