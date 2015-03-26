from Products.CMFCore.utils import getToolByName

from imio.history.config import DEFAULT_IGNORABLE_COMMENTS
from imio.history.config import HISTORY_COMMENT_NOT_VIEWABLE


class ImioHistoryAdapter(object):
    def __init__(self, context):
        self.context = context
        self.request = self.context.REQUEST

    def getHistory(self):
        """See docstring in interfaces.py."""
        res = []
        wfTool = getToolByName(self.context, 'portal_workflow')
        wfName = wfTool.getWorkflowsFor(self.context)[0].getId()
        history = list(self.context.workflow_history[wfName])
        history.reverse()
        for event in history:
            # hide comment if user may not access it
            if not self.mayViewComment(event):
                # We take a copy, because we will modify it.
                event = event.copy()
                event['comments'] = HISTORY_COMMENT_NOT_VIEWABLE
            res.append(event)
        return res

    def historyLastEventHasComments(self):
        """See docstring in interfaces.py."""
        history = self.getHistory()
        if not history:
            return False
        lastEvent = history[0]
        if not lastEvent['comments'] in self.ignorableHistoryComments():
            return True
        return False

    def ignorableHistoryComments(self):
        """See docstring in interfaces.py."""
        return DEFAULT_IGNORABLE_COMMENTS

    def mayViewComment(self, event):
        """See docstring in interfaces.py."""
        return True
