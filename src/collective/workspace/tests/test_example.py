from collective.workspace.testing import \
    COLLECTIVE_WORKSPACE_INTEGRATION_TESTING
from plone import api

import unittest

try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    # BBB for Plone 5.0 and lower.
    get_installer = None


class TestExample(unittest.TestCase):

    layer = COLLECTIVE_WORKSPACE_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        if get_installer is None:
            self.installer = api.portal.get_tool('portal_quickinstaller')
        else:
            self.installer = get_installer(self.portal)

    def test_product_is_installed(self):
        """ Validate that our products GS profile has been run and the product
            installed
        """
        pid = 'collective.workspace'
        if get_installer is None:
            is_installed = self.installer.isProductInstalled(pid)
        else:
            is_installed = self.installer.is_product_installed(pid)
        self.assertTrue(is_installed)
