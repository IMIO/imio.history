# -*- coding: utf-8 -*-
from zope.component import getAdapter, getAdapters

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.content import ContentHistoryView
from plone.app.layout.viewlets.content import DocumentBylineViewlet
from plone.memoize.view import memoize

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
        if transitionName and \
           hasattr(currentWF.transitions, transitionName) \
           and currentWF.transitions[transitionName].title:
            return currentWF.transitions[transitionName].title
        else:
            return transitionName

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
        if self.context.getTypeInfo().getId() in pr.getVersionableContentTypes():
            return True
        else:
            return False


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
