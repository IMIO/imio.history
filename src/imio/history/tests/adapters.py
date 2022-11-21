# -*- coding: utf-8 -*-

from imio.history.adapters import ImioRevisionHistoryAdapter
from imio.history.adapters import ImioWfHistoryAdapter
from imio.history.browser.views import IHContentHistoryView


class TestingImioWfHistoryAdapter(ImioWfHistoryAdapter):

    def mayViewEvent(self, event):
        """See docstring in interfaces.py."""
        if self.request.get('hide_wf_history_event', False) and \
           event['action'] == 'publish':
            return False
        return True

    def mayViewComment(self, event):
        """See docstring in interfaces.py."""
        if self.request.get('hide_wf_history_comment', False):
            return False
        return True


class TestingImioRevisionHistoryAdapter(ImioRevisionHistoryAdapter):

    def mayViewEvent(self, event):
        """See docstring in interfaces.py."""
        if self.request.get('hide_revisions_event', False):
            return False
        return True

    def mayViewComment(self, event):
        """See docstring in interfaces.py."""
        if self.request.get('hide_revisions_comment', False):
            return False
        return True


class TestingIHContentHistoryView(IHContentHistoryView):

    def show_preview(self, event):
        """ """
        return True
