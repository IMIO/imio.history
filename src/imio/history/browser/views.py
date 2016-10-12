# -*- coding: utf-8 -*-
from zope.component import getAdapter, getAdapters
from zope.i18n import translate

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.utils import safe_unicode
from plone.app.layout.viewlets.content import ContentHistoryView
from plone.app.layout.viewlets.content import DocumentBylineViewlet
from plone.memoize.view import memoize

from imio.history.config import HISTORY_REVISION_NOT_VIEWABLE
from imio.history.interfaces import IImioHistory


class IHDocumentBylineViewlet(DocumentBylineViewlet):
    """Overrides the DocumentBylineViewlet."""

    index = ViewPageTemplateFile("templates/document_byline.pt")

    def show_history(self):
        """
          Originally, the history is shown to people having the
          'CMFEditions: Access previous versions' permission, here
          we want everybody than can acces the object to see the history...
        """
        # do not show a link to the history if we are displaying something in a popup
        # because history is deiaplayed also in a popup...
        if 'ajax_load' in self.request:
            return False
        return True

    def highlight_history_link(self):
        """
          If a comment was added to last event of the object history,
          we highlight the link (set a css class on it) so user eye is drawn to it.
        """
        adapter = getAdapter(self.context, IImioHistory, 'workflow')
        return adapter.historyLastEventHasComments()


class IHContentHistoryView(ContentHistoryView):
    '''
      Overrides the ContentHistoryView template to use our own.
      We want to display the content_history as a table.
    '''
    index = ViewPageTemplateFile("templates/content_history.pt")

    def __init__(self, context, request):
        super(IHContentHistoryView, self).__init__(context, request)
        self.transformsTool = getToolByName(self.context, 'portal_transforms')

    def getHistory(self, checkMayView=True):
        """Get the history for current object.

        Merge workflow history with content history and sort by time."""
        history = []
        history_adapters = getAdapters((self.context,), IImioHistory)
        for adapter in history_adapters:
            history.extend(adapter[1].getHistory(checkMayView=checkMayView))

        if not history:
            return []

        history.sort(key=lambda x: x["time"], reverse=True)
        return history

    def getTransitionTitle(self, transitionName):
        """
          Given a p_transitionName, return the defined title in portal_workflow
          as it is what is really displayed in the template.
        """
        currentWF = self._getCurrentContextWorkflow()
        if transitionName in currentWF.transitions and \
           currentWF.transitions[transitionName].title:
            return currentWF.transitions[transitionName].title
        else:
            return transitionName

    def renderComments(self, comments):
        """
          Render comments correctly as it is 'plain/text' and we want 'text/html'.
        """
        # try to translate comments before it is turned into text/html
        translated = translate(safe_unicode(comments), domain='imio.history', context=self.request)
        data = self.transformsTool.convertTo('text/x-html-safe', translated)
        return data.getData()

    @memoize
    def _getCurrentContextWorkflow(self):
        """
          Return currently used workflow.
        """
        wfTool = getToolByName(self.context, 'portal_workflow')
        return wfTool.getWorkflowsFor(self.context)[0]

    def showColors(self):
        """
          Colorize transition name?
        """
        return True

    def showRevisionInfos(self):
        """Return True if the type of the context is versioned. """
        pr = getToolByName(self.context, 'portal_repository')
        if self.context.portal_type in pr.getVersionableContentTypes():
            return True
        else:
            return False

    def versionIsViewable(self, event):
        """
          Check if version we want to show is viewable.
        """
        return not bool(event['comments'] == HISTORY_REVISION_NOT_VIEWABLE)


class IHVersionPreviewView(BrowserView):
    """Makes it possible to display a preview of a given version."""

    def __init__(self, context, request):
        """ """
        super(IHVersionPreviewView, self).__init__(context, request)
        self.portal = getToolByName(self.context, 'portal_url').getPortalObject()
        self.portal_url = self.portal.absolute_url()

    def __call__(self, version_id):
        pr = getToolByName(self.context, 'portal_repository')
        self.versioned_object = pr.retrieve(self.context, version_id).object
        return super(IHVersionPreviewView, self).__call__()
