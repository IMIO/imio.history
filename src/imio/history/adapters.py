from Acquisition import aq_base

from Products.CMFCore.utils import getToolByName

from imio.history.config import DEFAULT_IGNORABLE_COMMENTS
from imio.history.config import HISTORY_COMMENT_NOT_VIEWABLE


class ImioHistoryAdapter(object):
    def __init__(self, context):
        self.context = context
        self.request = self.context.REQUEST

    def getHistory(self, checkMayView=True):
        """See docstring in interfaces.py."""
        res = []
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
        if checkMayView:
            for event in history:
                # hide comment if user may not access it
                if not self.mayViewComment(event):
                    # We take a copy, because we will modify it.
                    event = event.copy()
                    event['comments'] = HISTORY_COMMENT_NOT_VIEWABLE
                res.append(event)
        else:
            res = history
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
