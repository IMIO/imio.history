from Acquisition import aq_base

from Products.CMFCore.utils import getToolByName

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
        history = getattr(aq_base(self.context), 'workflow_history', None)
        if not history:
            return False
        # workflow_history is like :
        # {'my_content_workflow': ({'action': None, 'review_state': 'created', 'actor': 'admin',
        #                           'comments': 'My comment', 'time': DateTime('2014/06/05 14:35 GMT+2')},
        #  'my_content_former_workflow': ({'action': None, 'review_state': 'created', 'actor': 'admin',
        #                           'comments': 'My comment', 'time': DateTime('2012/02/02 12:00 GMT+2')}, }
        # if we have only one key in the history, we take relevant corresponding actions but if we have
        # several keys, we need to get current workflow and to reach relevant actions
        keys = history.keys()
        lastEvent = {'comments': ''}
        if len(keys) == 1:
            lastEvent = history[keys[0]][-1]
        elif len(keys) > 1:
            # get current workflow history
            wfTool = getToolByName(self.context, 'portal_workflow')
            contextWFs = wfTool.getWorkflowsFor(self.context)
            if not contextWFs:
                return False
            currentWFId = contextWFs[0].getId()
            lastEvent = history[currentWFId][-1]
        if not lastEvent['comments'] in self.ignorableHistoryComments():
            return True
        return False

    def ignorableHistoryComments(self):
        """See docstring in interfaces.py."""
        return ('', None, HISTORY_COMMENT_NOT_VIEWABLE)

    def mayViewComment(self, event):
        """See docstring in interfaces.py."""
        return True
