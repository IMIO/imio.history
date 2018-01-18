from Acquisition import aq_base

from plone import api
from plone.app.layout.viewlets.content import ContentHistoryViewlet

from imio.history.config import DEFAULT_IGNORABLE_COMMENTS
from imio.history.config import HISTORY_COMMENT_NOT_VIEWABLE
from imio.history.config import HISTORY_REVISION_NOT_VIEWABLE
from imio.history.utils import getLastAction


class BaseImioHistoryAdapter(object):

    """Base adapter for imio.history."""

    history_type = None
    history_attr_name = None
    comment_not_viewable_value = HISTORY_COMMENT_NOT_VIEWABLE

    def __init__(self, context):
        self.context = context
        self.request = self.context.REQUEST

    def get_history_data(self):
        """Overridable method that returns the base history to handle."""
        history = []
        if self.history_attr_name:
            history = getattr(self.context, 'emergency_changes_history', [])
        return history

    def getHistory(self,
                   checkMayViewEvent=True,
                   checkMayViewComment=True,
                   **kw):
        """Get an history."""
        history = self.get_history_data()
        res = []
        for event in history:
            # Make sure original event is not modified
            event = event.copy()
            if checkMayViewEvent and not self.mayViewEvent(event):
                continue
            if checkMayViewComment and not self.mayViewComment(event):
                event['comments'] = self.comment_not_viewable_value
            if self.history_type:
                event['type'] = self.history_type
            res.append(event)
        return res

    def mayViewComment(self, event):
        """See docstring in interfaces.py."""
        return True

    def mayViewEvent(self, event):
        """See docstring in interfaces.py."""
        return True


class ImioWfHistoryAdapter(BaseImioHistoryAdapter):

    """Adapter for workflow history."""

    history_type = 'workflow'

    def get_history_data(self):
        """ """
        history = []
        # no workflow_history attribute?  Return
        if not hasattr(aq_base(self.context), 'workflow_history'):
            return history
        wfTool = api.portal.get_tool('portal_workflow')
        wfs = wfTool.getWorkflowsFor(self.context)
        # no workflow currently used for the context?  Return
        if not wfs:
            return history
        wfName = wfTool.getWorkflowsFor(self.context)[0].getId()
        # in some case (we changed the workflow for already existing element
        # for example), the workflow key is not in workflow_history
        if wfName not in self.context.workflow_history:
            return history
        history = list(self.context.workflow_history[wfName])
        return history

    def historyLastEventHasComments(self):
        """See docstring in interfaces.py."""
        lastEvent = getLastAction(self.context)
        if lastEvent and lastEvent['comments'] not in self.ignorableHistoryComments():
            return True
        return False

    def ignorableHistoryComments(self):
        """See docstring in interfaces.py."""
        return DEFAULT_IGNORABLE_COMMENTS


class ImioRevisionHistoryAdapter(BaseImioHistoryAdapter, ContentHistoryViewlet):
    """Adapter for revision history."""

    comment_not_viewable_value = HISTORY_REVISION_NOT_VIEWABLE

    def __init__(self, context):
        self.context = context
        self.request = self.context.REQUEST
        self.site_url = api.portal.get().absolute_url()

    def get_history_data(self):
        """Get revision history."""
        history = self.revisionHistory()
        # only store actors fullnames
        for event in history:
            event['actor'] = event['actor']['fullname']
        return history
