# -*- coding: utf-8 -*-

from imio.history.testing import IntegrationTestCase
from Products.CMFCore.utils import getToolByName


class TestSetup(IntegrationTestCase):

    def test_product_is_installed(self):
        """ Validate that our products GS profile has been run and the product installed."""
        pid = 'imio.history'
        qi_tool = getToolByName(self.portal, 'portal_quickinstaller')
        installed = [p['id'] for p in qi_tool.listInstalledProducts()]
        self.assertTrue(pid in installed,
                        'package appears not to have been installed')
