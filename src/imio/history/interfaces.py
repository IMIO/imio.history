# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest


class IImioHistoryLayer(IBrowserRequest):
    """imio.history BrowserLayer interface."""
    pass


class IImioHistory(Interface):
    """ """

    def getHistory(self):
        """Returns the history for given p_obj, sorted in reverse order
        (most recent change first)."""

    def historyLastEventHasComments(self):
        """Returns True if the last event of the object's history has a comment."""

    def ignorableHistoryComments(self):
        """Ignorable history comments, stored as utf-8."""

    def mayViewComment(self, event):
        """This will make it possible to hide some comments."""
