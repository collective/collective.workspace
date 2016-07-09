from collective.workspace.testing import \
    COLLECTIVE_WORKSPACE_INTEGRATION_TESTING
import unittest2 as unittest


class TestExample(unittest.TestCase):

    layer = COLLECTIVE_WORKSPACE_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.qi_tool = self.portal.portal_quickinstaller

    def test_product_is_installed(self):
        """ Validate that our products GS profile has been run and the product
            installed
        """
        pid = 'collective.workspace'
        installed = [p['id'] for p in self.qi_tool.listInstalledProducts()]
        self.assertTrue(pid in installed,
                        'package appears not to have been installed')
