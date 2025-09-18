# -*- coding: utf-8 -*-

from imio.history.testing import IntegrationTestCase
from plone.base.utils import get_installer


class TestSetup(IntegrationTestCase):

    def test_product_is_installed(self):
        """Validate that our products GS profile has been run and the product installed."""
        installer = get_installer(self.portal, self.layer["request"])
        self.assertTrue(installer.is_product_installed("imio.history"))
