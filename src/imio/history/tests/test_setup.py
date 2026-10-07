# -*- coding: utf-8 -*-

from imio.history.interfaces import IImioHistoryLayer
from imio.history.testing import IntegrationTestCase
from imio.history.testing import plone6_bug
from imio.history.testing import PLONE_MAJOR
from plone import api
from plone.browserlayer.utils import registered_layers
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

import unittest


try:
    from plone.base.utils import get_installer
except ImportError:  # Plone 4: portal_quickinstaller, no uninstall profile
    get_installer = None


CSS_ID = "++resource++imio.history/imiohistory.css"
# Plone's byline viewlet, hidden by the default profile
PLONE_BYLINE = (
    "plone.documentbyline"
    if PLONE_MAJOR >= 6
    else "plone.belowcontenttitle.documentbyline"
)


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
        if get_installer is None:
            installer = api.portal.get_tool("portal_quickinstaller")
            self.assertTrue(installer.isProductInstalled("imio.history"))
        else:
            installer = get_installer(self.portal, self.layer["request"])
            self.assertTrue(installer.is_product_installed("imio.history"))

    def test_default_profile(self):
        """Browser layer, CSS, and the imio byline instead of Plone's one."""
        self.assertIn(IImioHistoryLayer, registered_layers())
        if PLONE_MAJOR >= 6:
            registry = getUtility(IRegistry)
            self.assertEqual(
                registry["plone.bundles/imio-history.csscompilation"], CSS_ID
            )
            self.assertTrue(registry["plone.bundles/imio-history.enabled"])
        else:
            css = api.portal.get_tool("portal_css").getResource(CSS_ID)
            self.assertTrue(css.getEnabled())
        self.assertEqual(self._byline_viewlets(), ["imio.history.documentbyline"])

    @unittest.skipIf(get_installer is None, "uninstall profile added on Plone 6")
    def test_uninstall_profile(self):
        installer = get_installer(self.portal, self.layer["request"])
        installer.uninstall_product("imio.history")
        self.assertFalse(installer.is_product_installed("imio.history"))
        self.assertNotIn(IImioHistoryLayer, registered_layers())
        registry = getUtility(IRegistry)
        self.assertNotIn("plone.bundles/imio-history.csscompilation", registry)

    @unittest.skipIf(get_installer is None, "uninstall profile added on Plone 6")
    @plone6_bug
    def test_uninstall_profile_shows_plone_byline(self):
        """profiles/uninstall/viewlets.xml has <orger> instead of <order>:
        Plone's byline stays hidden."""
        installer = get_installer(self.portal, self.layer["request"])
        installer.uninstall_product("imio.history")
        self.assertIn(PLONE_BYLINE, self._byline_viewlets())
