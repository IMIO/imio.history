# -*- coding: utf-8 -*-
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest


class IImioHistoryLayer(IBrowserRequest):

    """imio.history BrowserLayer interface."""

    pass


class IImioHistory(Interface):

    """Base interface for history adapters."""

    def getHistory(self, checkMayView=True, **kw):
        """Get history."""


class IImioWfHistory(IImioHistory):

    """Workflow history."""

    def getHistory(self, checkMayView=True, **kw):
        """Returns the history for context.  If p_checkMayView is True (default),
        the method 'mayViewComment' is called on every history event.
        If p_for_last_event is True, it means that getHistory is called from method
        historyLastEventHasComments.  This is done so when overrided, heavy process
        may be avoided when knowing that we will just get last event's comment."""

    def historyLastEventHasComments(self):
        """Returns True if the last event of the object's history has a comment."""

    def ignorableHistoryComments(self):
        """Ignorable history comments, stored as utf-8."""

    def mayViewComment(self, event):
        """This will make it possible to hide some comments."""


class IImioRevisionHistory(IImioHistory):

    """Revision history."""

    def getHistory(self, checkMayView=True, **kw):
        """Returns the history for context."""
