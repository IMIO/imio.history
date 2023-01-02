# -*- coding: utf-8 -*-

from Acquisition import aq_base
from imio.history.config import DEFAULT_IGNORABLE_COMMENTS
from imio.history.config import HISTORY_COMMENT_NOT_VIEWABLE
from imio.history.config import HISTORY_REVISION_NOT_VIEWABLE
from imio.history.utils import getLastAction
from plone import api
from plone.app.layout.viewlets.content import ContentHistoryViewlet
from plone.memoize.instance import memoize
from Products.CMFPlone.utils import safe_unicode


class BaseImioHistoryAdapter(object):

    """Base adapter for imio.history."""

    history_type = None
    history_attr_name = None
    comment_not_viewable_value = HISTORY_COMMENT_NOT_VIEWABLE
    highlight_last_comment = False

    def __init__(self, context):
        self.context = context
        self.request = self.context.REQUEST

    @memoize
    def get_history_data(self):
        """Overridable method that returns the base history to handle."""
        history = []
        if self.history_attr_name:
            history = getattr(self.context, self.history_attr_name, [])
        return history

    @memoize
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
            if self.history_type:
                event['type'] = self.history_type

            if checkMayViewEvent and not self.mayViewEvent(event):
                continue
            if checkMayViewComment and not self.mayViewComment(event):
                event['comments'] = self.comment_not_viewable_value
            res.append(event)
        return res

    def mayViewComment(self, event):
        """See docstring in interfaces.py."""
        return True

    def mayViewEvent(self, event):
        """See docstring in interfaces.py."""
        return True

    def historyLastEventHasComments(self):
        """See docstring in interfaces.py."""
        if self.highlight_last_comment:
            # for performance reasons, we use checkMayViewEvent=False, checkMayViewComment=False
            # this will do sometimes highlight history in red and last comment is not viewable...
            lastEvent = getLastAction(self)
            if lastEvent and \
               lastEvent['comments'] and \
               safe_unicode(lastEvent['comments']) not in self.ignorableHistoryComments():
                return True
        return False

    def ignorableHistoryComments(self):
        """See docstring in interfaces.py."""
        return DEFAULT_IGNORABLE_COMMENTS


class ImioWfHistoryAdapter(BaseImioHistoryAdapter):

    """Adapter for workflow history."""

    history_type = 'workflow'
    include_previous_review_state = False
    highlight_last_comment = True

    @memoize
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
        if self.include_previous_review_state:
            history = self._build_history_with_previous_review_state(history)
        return history

    def _build_history_with_previous_review_state(self, history_data):
        """Include 'previous_review_state' key in every hisotry event."""
        res = []
        previous_event = None
        for event in history_data:
            new_event = event.copy()
            new_event['previous_review_state'] = previous_event and previous_event['review_state'] or None
            previous_event = new_event.copy()
            res.append(new_event)
        return res


class ImioRevisionHistoryAdapter(BaseImioHistoryAdapter, ContentHistoryViewlet):
    """Adapter for revision history."""

    comment_not_viewable_value = HISTORY_REVISION_NOT_VIEWABLE

    def __init__(self, context):
        self.context = context
        self.request = self.context.REQUEST
        self.site_url = api.portal.get().absolute_url()

    @memoize
    def get_history_data(self):
        """Get revision history."""
        history = self.revisionHistory()
        # only store actors fullnames
        for event in history:
            event['actor'] = event['actor']['fullname']
        return history
