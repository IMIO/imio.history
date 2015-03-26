from zope.component import getMultiAdapter
from zope.viewlet.interfaces import IViewletManager

from Products.Five.browser import BrowserView

from plone import api
from imio.history.config import HISTORY_COMMENT_NOT_VIEWABLE
from imio.history.interfaces import IImioHistory
from imio.history.testing import IntegrationTestCase


class TestDocumentByLineViewlet(IntegrationTestCase):

    def setUp(self):
        super(TestDocumentByLineViewlet, self).setUp()
        # get the viewlet
        doc = api.content.create(type='Document',
                                 id='doc',
                                 container=self.portal)
        view = BrowserView(doc, self.portal.REQUEST)
        manager = getMultiAdapter(
            (self.portal, self.portal.REQUEST, view),
            IViewletManager,
            'plone.belowcontenttitle')
        manager.update()
        self.viewlet = manager.get(u'imio.history.documentbyline')

    def test_show_history(self):
        """Test the show_history method.
           The history is shown in every case except if 'ajax_load' is found in the REQUEST."""
        self.assertTrue(self.viewlet.show_history())
        # show_history is False if displayed in a popup, aka 'ajax_load' in the REQUEST
        self.portal.REQUEST.set('ajax_load', True)
        self.assertFalse(self.viewlet.show_history())

    def test_highlight_history_link(self):
        """Test the highlight_history_link method.
           History link will be highlighted if last event had a comment and
           if that comment is not an ignorable comment."""
        adapter = IImioHistory(self.portal.doc)
        # historyLastEventHasComments will return False because '' is an ignored comment
        history = adapter.getHistory()
        self.assertFalse(adapter.historyLastEventHasComments())
        self.assertTrue(history[0]['comments'] in adapter.ignorableHistoryComments())

        # now 'publish' the doc and add a comment, last event has a comment
        self.wft.doActionFor(self.portal.doc, 'publish', comment='my publish comment')
        history = adapter.getHistory()
        self.assertTrue(adapter.historyLastEventHasComments())
        self.assertFalse(history[0]['comments'] in adapter.ignorableHistoryComments())

        # now test the 'you can not access this comment' message
        self.wft.doActionFor(self.portal.doc, 'retract', comment=HISTORY_COMMENT_NOT_VIEWABLE)
        history = adapter.getHistory()
        self.assertFalse(adapter.historyLastEventHasComments())
        self.assertTrue(history[0]['comments'] in adapter.ignorableHistoryComments())
