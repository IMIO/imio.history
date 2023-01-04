# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest


class IImioHistoryLayer(IBrowserRequest):

    """imio.history BrowserLayer interface."""

    pass


class IImioHistory(Interface):

    """Base interface for history adapters."""

    def getHistory(self, checkMayViewEvent=True, checkMayViewComment=True, **kw):
        """Get an history. p_checkMayViewEvent will check if event is viewable and
           p_checkMayViewComment will check if the comment of an event is viewable."""

    def get_history_data(self):
        """Base overridable method that returns the base history to handle."""

    def mayViewEvent(self, event):
        """This will make it possible to hide some complete events."""

    def mayViewComment(self, event):
        """This will make it possible to hide some comments."""

    def historyLastEventHasComments(self):
        """Returns True if the last event of the object's history has a comment.
           Ideally, this method should return a list of unicode so comparison
           with comments is possible."""

    def ignorableHistoryComments(self):
        """Ignorable history comments, stored as utf-8."""


class IImioWfHistory(IImioHistory):

    """Workflow history."""

    def getHistory(self, checkMayViewEvent=True, checkMayViewComment=True, **kw):
        """Returns the WF history for context."""


class IImioRevisionHistory(IImioHistory):

    """Revision history."""

    def getHistory(self, checkMayViewEvent=True, checkMayViewComment=True, **kw):
        """Returns the history for context."""
