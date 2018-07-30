# -*- coding: utf-8 -*-

from imio import history as imio_history
from imio.history.config import HISTORY_REVISION_NOT_VIEWABLE
from imio.history.interfaces import IImioHistory
from imio.history.testing import IntegrationTestCase
from plone import api
from plone.app.testing import TEST_USER_NAME
from Products.Five import zcml
from zope.component import getAdapter
from zope.component import getMultiAdapter


class TestImioRevisionHistoryAdapter(IntegrationTestCase):

    """Test ImioRevisionHistoryAdapter."""

    def setUp(self):
        super(TestImioRevisionHistoryAdapter, self).setUp()
        doc = api.content.create(type='Document',
                                 id='doc',
                                 container=self.portal)
        self.doc = doc

    def test_getHistory(self):
        adapter = getAdapter(self.doc, IImioHistory, 'revision')
        history = adapter.getHistory()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['type'], 'versioning')
        self.assertEqual(history[0]['actor'], TEST_USER_NAME)
        self.assertEqual(history[0]['action'], 'Edited')

    def test_MayViewVersionComment(self, ):
        """Test the mayViewComment method.
           We will register an adapter that test when it is overrided."""
        # by default, mayViewComment returns "True" so every revisions
        # are viewable in the object's history
        # use self.doc and make a new revision, the revision is viewable
        view = getMultiAdapter((self.doc, self.portal.REQUEST), name='contenthistory')
        history = view.getHistory()
        # as versioning is active for documents, a revision is already available
        pr = self.portal.portal_repository
        self.assertTrue(self.doc.meta_type in pr.getVersionableContentTypes())
        lastEvent = history[0]
        self.assertEqual(lastEvent['action'], u'Edited')
        self.assertEqual(lastEvent['comments'], u'Initial revision')
        self.assertTrue(view.versionIsViewable(lastEvent))

        # now register an adapter that will do 'Initial revision' comment not visible
        zcml.load_config('testing-adapter.zcml', imio_history)
        self.request.set('hide_revisions_comment', True)
        history = view.getHistory()
        lastEvent = history[0]
        self.assertEqual(lastEvent['action'], u'Edited')
        self.assertEqual(lastEvent['comments'], HISTORY_REVISION_NOT_VIEWABLE)
        self.assertFalse(view.versionIsViewable(lastEvent))

        # getHistory can be called with checkMayViewComment set to False,
        # in this case, mayViewVersion check is not done
        history = view.getHistory(checkMayViewComment=False)
        lastEvent = history[0]
        self.assertEqual(lastEvent['action'], u'Edited')
        self.assertEqual(lastEvent['comments'], u'Initial revision')
        # cleanUp zmcl.load_config because it impact other tests
        zcml.cleanUp()
