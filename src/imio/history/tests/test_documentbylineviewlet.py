# -*- coding: utf-8 -*-

from imio.history.config import HISTORY_COMMENT_NOT_VIEWABLE
from imio.history.interfaces import IImioHistory
from imio.history.testing import IntegrationTestCase
from plone import api
from plone.memoize.instance import Memojito
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.viewlet.interfaces import IViewletManager


class TestDocumentByLineViewlet(IntegrationTestCase):

    def setUp(self):
        super(TestDocumentByLineViewlet, self).setUp()
        # get the viewlet
        doc = api.content.create(type='Document',
                                 id='doc',
                                 container=self.portal)
        view = doc.restrictedTraverse('@@folder_contents')
        manager = getMultiAdapter(
            (doc, self.portal.REQUEST, view),
            IViewletManager,
            'plone.belowcontenttitle')
        manager.update()
        self.viewlet = manager.get(u'imio.history.documentbyline')
        self.viewlet.update()
        self.viewlet.render()

    def test_show_history(self):
        """Test the show_history method.  Shown by default."""
        self.assertTrue(self.viewlet.show_history())
        # show_history is also displayed in a popup, aka 'ajax_load' in the REQUEST
        self.portal.REQUEST.set('ajax_load', True)
        self.assertTrue(self.viewlet.show_history())

    def test_highlight_history_link(self):
        """Test the highlight_history_link method.
           History link will be highlighted if last event had a comment and
           if that comment is not an ignorable comment."""
        adapter = getAdapter(self.portal.doc, IImioHistory, 'workflow')
        # not highlighted because '' is an ignored comment
        history = adapter.getHistory()
        self.assertFalse(history[-1]['comments'])
        self.assertFalse(self.viewlet.highlight_history_link())

        # now 'publish' the doc and add a comment, last event has a comment
        self.wft.doActionFor(self.portal.doc, 'publish', comment='my publish comment')
        # clean memoize
        getattr(adapter, Memojito.propname).clear()
        history = adapter.getHistory()
        self.assertTrue(self.viewlet.highlight_history_link())
        self.assertFalse(history[-1]['comments'] in adapter.ignorableHistoryComments())

        # now test that the 'you can not access this comment' is an ignored message
        self.wft.doActionFor(self.portal.doc, 'retract', comment=HISTORY_COMMENT_NOT_VIEWABLE)
        getattr(adapter, Memojito.propname).clear()
        history = adapter.getHistory()
        self.assertFalse(self.viewlet.highlight_history_link())
        self.assertTrue(history[-1]['comments'] in adapter.ignorableHistoryComments())

        # test that it works if no history
        # it is the case if we changed used workflow
        self.wft.setChainForPortalTypes(('Document', ), ('intranet_workflow',))
        getattr(adapter, Memojito.propname).clear()
        history = adapter.getHistory()
        self.assertFalse(self.viewlet.highlight_history_link())
        self.assertTrue(history == [])
