from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE
from plone.testing import z2

from zope.configuration import xmlconfig


class CollectiveWorkspaceLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import collective.workspace
        xmlconfig.file(
            'configure.zcml',
            collective.workspace,
            context=configurationContext
        )

        z2.installProduct(app, 'collective.workspace')

    def tearDownZope(self, app):
        # Uninstall products installed above
        z2.uninstallProduct(app, 'collective.workspace')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.workspace:default')

        # Create a content type with the behavior enabled
        from plone.dexterity.fti import DexterityFTI
        fti = DexterityFTI('Workspace')
        fti.behaviors = (
            'plone.app.content.interfaces.INameFromTitle',
            'plone.app.dexterity.behaviors.metadata.IBasic',
            'collective.workspace.interfaces.IWorkspace',
            )
        portal.portal_types._setObject('Workspace', fti)


COLLECTIVE_WORKSPACE_FIXTURE = CollectiveWorkspaceLayer()
COLLECTIVE_WORKSPACE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_WORKSPACE_FIXTURE,),
    name="CollectiveWorkspaceLayer:Integration"
)
COLLECTIVE_WORKSPACE_ROBOT_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_WORKSPACE_FIXTURE, AUTOLOGIN_LIBRARY_FIXTURE, z2.ZSERVER),
    name="CollectiveWorkspaceLayer:Robot"
)
