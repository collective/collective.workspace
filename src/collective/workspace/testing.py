# coding=utf-8
from plone import api
from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from zope.configuration import xmlconfig


try:
    from plone.testing import zope
except ImportError:
    from plone.testing import z2 as zope


try:
    from plone.testing.zope import WSGI_SERVER_FIXTURE
except ImportError:
    from plone.testing.z2 import ZSERVER_FIXTURE as WSGI_SERVER_FIXTURE


class CollectiveWorkspaceLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import collective.workspace

        xmlconfig.file(
            "configure.zcml", collective.workspace, context=configurationContext
        )
        zope.installProduct(app, "collective.workspace")

    def tearDownZope(self, app):
        # Uninstall products installed above
        zope.uninstallProduct(app, "collective.workspace")

    def setUpPloneSite(self, portal):
        applyProfile(portal, "collective.workspace:default")

        # Create a content type with the behavior enabled
        from plone.dexterity.fti import DexterityFTI

        fti = DexterityFTI("Workspace")
        fti.behaviors = (
            "plone.namefromtitle",
            "plone.basic",
            "collective.workspace.team_workspace",
        )
        portal.portal_types._setObject("Workspace", fti)
        api.user.get("test_user_1_").setProperties({"fullname": "Test user"})


COLLECTIVE_WORKSPACE_FIXTURE = CollectiveWorkspaceLayer()
COLLECTIVE_WORKSPACE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_WORKSPACE_FIXTURE,), name="CollectiveWorkspaceLayer:Integration"
)
COLLECTIVE_WORKSPACE_ROBOT_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_WORKSPACE_FIXTURE,
        AUTOLOGIN_LIBRARY_FIXTURE,
        WSGI_SERVER_FIXTURE,
    ),
    name="CollectiveWorkspaceLayer:Robot",
)
