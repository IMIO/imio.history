# -*- coding: utf-8 -*-
from zope.component import getAdapter
from plone import api
from plone.app.testing import TEST_USER_NAME

from imio.history.interfaces import IImioHistory
from imio.history.testing import IntegrationTestCase


class TestImioRevisionHistoryAdapter(IntegrationTestCase):

    """Test ImioRevisionHistoryAdapter."""

    def test_getHistory(self):
        doc = api.content.create(
            type='Document',
            id='doc',
            container=self.portal)
        adapter = getAdapter(doc, IImioHistory, 'revision')
        history = adapter.getHistory()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['type'], 'versioning')
        self.assertEqual(history[0]['actor'], TEST_USER_NAME)
        self.assertEqual(history[0]['action'], 'Edited')
