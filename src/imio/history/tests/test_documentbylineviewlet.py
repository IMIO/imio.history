# -*- coding: utf-8 -*-

from imio.history.config import HISTORY_COMMENT_NOT_VIEWABLE
from imio.history.interfaces import IImioHistory
from imio.history.testing import IntegrationTestCase
from imio.history.testing import plone6_bug
from plone import api
from plone.app.testing import login
from plone.memoize.instance import Memojito
from zope.component import getAdapter

import re


class TestDocumentByLineViewlet(IntegrationTestCase):

    def setUp(self):
        super(TestDocumentByLineViewlet, self).setUp()
        api.content.create(type="Document", id="doc", container=self.portal)
        self.viewlet = self._viewlet()
        self.viewlet.render()

    def _viewlet(self):
        """The byline viewlet of the doc, for the current user."""
        manager = self.below_content_title(self.portal.doc)
        viewlet = manager.get("imio.history.documentbyline")
        viewlet.update()
        return viewlet

    def test_render(self):
        """Author without link, History link to @@historyview, highlighted after a comment."""
        html = self.viewlet.render()
        self.assertIn('<span class="documentAuthor">', html)
        self.assertNotIn("/author/", html)
        self.assertIn('<span class="contentHistory" id="content-history">', html)
        self.assertIn('href="http://nohost/plone/doc/@@historyview"', html)
        self.wft.doActionFor(self.portal.doc, "publish", comment="my publish comment")
        html = self._viewlet().render()
        self.assertIn(
            '<span class="contentHistory highlight-history-link" id="content-history">',
            html,
        )

    @plone6_bug
    def test_history_link_viewable_without_modify_permission(self):
        """A Reviewer may access previous versions but not modify a published document:
        the History link is shown to him and he may open it.
        Plone 6: @@historyview requires "Modify portal content"."""
        doc = self.portal.doc
        self.wft.doActionFor(doc, "publish")
        api.user.create(
            email="reviewer@example.org",
            username="reviewer",
            password="reviewer-secret",
            roles=("Member", "Reviewer"),
        )
        login(self.portal, "reviewer")
        self.assertFalse(api.user.has_permission("Modify portal content", obj=doc))
        html = self._viewlet().render()
        href = re.search(r'id="content-history">.*?href="([^"]+)"', html, re.S).group(1)
        path = str(href.replace(self.portal.absolute_url() + "/", ""))
        self.assertTrue(self.portal.restrictedTraverse(path))

    def test_show_history(self):
        """Test the show_history method.  Shown by default."""
        self.assertTrue(self.viewlet.show_history())
        # show_history is also displayed in a popup, aka 'ajax_load' in the REQUEST
        self.portal.REQUEST.set("ajax_load", True)
        self.assertTrue(self.viewlet.show_history())

    def test_highlight_history_link(self):
        """Test the highlight_history_link method.
        History link will be highlighted if last event had a comment and
        if that comment is not an ignorable comment."""
        adapter = getAdapter(self.portal.doc, IImioHistory, "workflow")
        # not highlighted because '' is an ignored comment
        history = adapter.getHistory()
        self.assertFalse(history[-1]["comments"])
        self.assertFalse(self.viewlet.highlight_history_link())

        # now 'publish' the doc and add a comment, last event has a comment
        self.wft.doActionFor(self.portal.doc, "publish", comment="my publish comment")
        # clean memoize
        getattr(adapter, Memojito.propname).clear()
        history = adapter.getHistory()
        self.assertTrue(self.viewlet.highlight_history_link())
        self.assertFalse(history[-1]["comments"] in adapter.ignorableHistoryComments())

        # now test that the 'you can not access this comment' is an ignored message
        self.wft.doActionFor(
            self.portal.doc, "retract", comment=HISTORY_COMMENT_NOT_VIEWABLE
        )
        getattr(adapter, Memojito.propname).clear()
        history = adapter.getHistory()
        self.assertFalse(self.viewlet.highlight_history_link())
        self.assertTrue(history[-1]["comments"] in adapter.ignorableHistoryComments())

        # test that it works if no history
        # it is the case if we changed used workflow
        self.wft.setChainForPortalTypes(("Document",), ("intranet_workflow",))
        getattr(adapter, Memojito.propname).clear()
        history = adapter.getHistory()
        self.assertFalse(self.viewlet.highlight_history_link())
        self.assertTrue(history == [])
