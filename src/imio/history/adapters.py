from Acquisition import aq_base

from Products.CMFCore.utils import getToolByName
from plone import api
from plone.app.layout.viewlets.content import ContentHistoryViewlet

from imio.history.config import DEFAULT_IGNORABLE_COMMENTS
from imio.history.config import HISTORY_COMMENT_NOT_VIEWABLE


class ImioWfHistoryAdapter(object):

    """Adapter for workflow history."""

    def __init__(self, context):
        self.context = context
        self.request = self.context.REQUEST

    def getHistory(self, **kw):
        """See docstring in interfaces.py."""
        res = []
        if 'checkMayView' in kw:
            checkMayView = kw['checkMayView']
        else:
            checkMayView = True

        # no workflow_history attribute?  Return
        if not hasattr(aq_base(self.context), 'workflow_history'):
            return res
        wfTool = getToolByName(self.context, 'portal_workflow')
        wfs = wfTool.getWorkflowsFor(self.context)
        # no workflow currently used for the context?  Return
        if not wfs:
            return res
        wfName = wfTool.getWorkflowsFor(self.context)[0].getId()
        # in some case (we changed the workflow for already existing element
        # for example), the workflow key is not in workflow_history
        if not wfName in self.context.workflow_history:
            return res
        history = list(self.context.workflow_history[wfName])

        for event in history:
            # We take a copy, because we will modify it.
            event = event.copy()
            if checkMayView and not self.mayViewComment(event):
                event['comments'] = HISTORY_COMMENT_NOT_VIEWABLE

            event['type'] = 'workflow'
            res.append(event)

        return res

    def historyLastEventHasComments(self):
        """See docstring in interfaces.py."""
        history = self.getHistory()
        if not history:
            return False
        lastEvent = history[-1]
        if not lastEvent['comments'] in self.ignorableHistoryComments():
            return True
        return False

    def ignorableHistoryComments(self):
        """See docstring in interfaces.py."""
        return DEFAULT_IGNORABLE_COMMENTS

    def mayViewComment(self, event):
        """See docstring in interfaces.py."""
        return True


class ImioRevisionHistoryAdapter(ContentHistoryViewlet):

    """Adapter for revision history."""

    def __init__(self, context):
        self.context = context
        self.request = self.context.REQUEST
        self.site_url = api.portal.get().absolute_url()

    def getHistory(self, **kw):
        """Get revision history."""
        history = self.revisionHistory()
        # only store actors fullnames
        for event in history:
            event['actor'] = event['actor']['fullname']

        return history
