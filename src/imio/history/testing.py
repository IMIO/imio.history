# -*- coding: utf-8 -*-

from plone.app.layout.globals.interfaces import IViewView
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.testing import zope
from Products.CMFPlone.utils import getFSVersionTuple
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.viewlet.interfaces import IViewletManager

import imio.history
import unittest


PLONE_MAJOR = getFSVersionTuple()[0]


def plone6_bug(test_method):
    """Expected failure on Plone 6: bug of the Plone 6 port, pinned until it is fixed."""
    if PLONE_MAJOR >= 6:
        return unittest.expectedFailure(test_method)
    return test_method


class PloneWithHistoryLayer(PloneWithPackageLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        # Load ZCML
        self.loadZCML(package=imio.history, name="testing.zcml")
        zope.installProduct(app, "imio.history")

    def setUpPloneSite(self, portal):
        """Set up Plone."""
        # Install into Plone site using portal_setup
        applyProfile(portal, "imio.history:testing")

        # Login and create some test content
        setRoles(portal, TEST_USER_ID, ["Manager"])
        login(portal, TEST_USER_NAME)
        folder_id = portal.invokeFactory("Folder", "folder")
        portal[folder_id].reindexObject()

        # make sure we have a default workflow
        portal.portal_workflow.setDefaultChain("simple_publication_workflow")

        # Commit so that the test browser sees these objects
        import transaction

        transaction.commit()

    def tearDownZope(self, app):
        """Tear down Zope."""
        zope.uninstallProduct(app, "imio.history")


FIXTURE = PloneWithHistoryLayer(name="FIXTURE")


INTEGRATION = IntegrationTesting(bases=(FIXTURE,), name="INTEGRATION")


FUNCTIONAL = FunctionalTesting(bases=(FIXTURE,), name="FUNCTIONAL")


ACCEPTANCE = FunctionalTesting(
    bases=(FIXTURE, REMOTE_LIBRARY_BUNDLE_FIXTURE, zope.WSGI_SERVER_FIXTURE),
    name="ACCEPTANCE",
)


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION

    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.catalog = self.portal.portal_catalog
        self.wft = self.portal.portal_workflow

    def below_content_title(self, obj):
        """plone.belowcontenttitle viewlet manager of the obj view, for the current user."""
        view = BrowserView(obj, self.portal.REQUEST)
        alsoProvides(view, IViewView)
        manager = getMultiAdapter(
            (obj, self.portal.REQUEST, view), IViewletManager, "plone.belowcontenttitle"
        )
        manager.update()
        return manager


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL

    def setUp(self):
        super(FunctionalTestCase, self).setUp()
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.catalog = self.portal.portal_catalog
        self.wft = self.portal.portal_workflow
