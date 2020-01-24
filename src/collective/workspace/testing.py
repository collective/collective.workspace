# coding=utf-8
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE
from plone.testing import zope
from plone import api
from zope.configuration import xmlconfig


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
        zope.WSGI_SERVER_FIXTURE,
    ),
    name="CollectiveWorkspaceLayer:Robot",
)
