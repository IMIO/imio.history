# -*- coding: utf-8 -*-

from imio.history.interfaces import IImioHistory
from imio.history.testing import IntegrationTestCase
from plone import api
from plone.app.testing import TEST_USER_ID
from zope.component import getAdapter


class TestImioWFHistoryAdapter(IntegrationTestCase):

    """Test ImioWFHistoryAdapter."""

    def setUp(self):
        super(TestImioWFHistoryAdapter, self).setUp()
        doc = api.content.create(type='Document',
                                 id='doc',
                                 container=self.portal)
        self.doc = doc

    def test_getHistory(self):
        adapter = getAdapter(self.doc, IImioHistory, 'workflow')
        self.wft.doActionFor(self.doc, 'publish')
        history = adapter.getHistory()
        self.assertEqual(len(history), 2)
        # creation event
        creation_event = history[0]
        self.assertEqual(creation_event['type'], 'workflow')
        self.assertEqual(creation_event['review_state'], 'private')
        self.assertEqual(creation_event['actor'], TEST_USER_ID)
        self.assertIsNone(creation_event['action'])
        # creation event
        publish_event = history[1]
        self.assertEqual(publish_event['type'], 'workflow')
        self.assertEqual(publish_event['review_state'], 'published')
        self.assertEqual(publish_event['actor'], TEST_USER_ID)
        self.assertEqual(publish_event['action'], 'publish')

    def test_getHistoryWithPreviousReviewState(self):
        """ """
        adapter = getAdapter(self.doc, IImioHistory, 'workflow')
        self.wft.doActionFor(self.doc, 'publish')
        self.assertFalse(adapter.include_previous_review_state)
        adapter.include_previous_review_state = True
        history = adapter.getHistory()
        # creation event
        creation_event = history[0]
        self.assertEqual(creation_event['type'], 'workflow')
        self.assertEqual(creation_event['review_state'], 'private')
        self.assertEqual(creation_event['actor'], TEST_USER_ID)
        self.assertIsNone(creation_event['action'])
        self.assertIsNone(creation_event['previous_review_state'])
        # creation event
        publish_event = history[1]
        self.assertEqual(publish_event['type'], 'workflow')
        self.assertEqual(publish_event['review_state'], 'published')
        self.assertEqual(publish_event['actor'], TEST_USER_ID)
        self.assertEqual(publish_event['action'], 'publish')
        self.assertEqual(publish_event['previous_review_state'], 'private')
