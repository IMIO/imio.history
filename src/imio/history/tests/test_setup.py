# -*- coding: utf-8 -*-

from imio.history.interfaces import IImioHistoryLayer
from imio.history.testing import IntegrationTestCase
from plone import api
from plone.base.utils import get_installer
from plone.browserlayer.utils import registered_layers
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


CSS_ID = "++resource++imio.history/imiohistory.css"
# Plone's byline viewlet, hidden by the default profile
PLONE_BYLINE = "plone.documentbyline"


class TestSetup(IntegrationTestCase):

    def _byline_viewlets(self):
        """Names of the byline viewlets rendered under the title of a document."""
        doc = api.content.create(type="Document", id="doc", container=self.portal)
        manager = self.below_content_title(doc)
        manager.render()
        return [
            viewlet.__name__
            for viewlet in manager.viewlets
            if viewlet.__name__.endswith("documentbyline")
        ]

    def test_product_is_installed(self):
        """Validate that our products GS profile has been run and the product installed."""
        installer = get_installer(self.portal, self.layer["request"])
        self.assertTrue(installer.is_product_installed("imio.history"))

    def test_default_profile(self):
        """Browser layer, CSS, and the imio byline instead of Plone's one."""
        self.assertIn(IImioHistoryLayer, registered_layers())
        registry = getUtility(IRegistry)
        self.assertEqual(registry["plone.bundles/imio-history.csscompilation"], CSS_ID)
        self.assertTrue(registry["plone.bundles/imio-history.enabled"])
        self.assertEqual(self._byline_viewlets(), ["imio.history.documentbyline"])

    def test_uninstall_profile(self):
        installer = get_installer(self.portal, self.layer["request"])
        installer.uninstall_product("imio.history")
        self.assertFalse(installer.is_product_installed("imio.history"))
        self.assertNotIn(IImioHistoryLayer, registered_layers())
        registry = getUtility(IRegistry)
        self.assertNotIn("plone.bundles/imio-history.csscompilation", registry)

    def test_uninstall_profile_shows_plone_byline(self):
        """Plone's byline is shown again."""
        installer = get_installer(self.portal, self.layer["request"])
        installer.uninstall_product("imio.history")
        self.assertIn(PLONE_BYLINE, self._byline_viewlets())
