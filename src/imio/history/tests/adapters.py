from imio.history.adapters import ImioWfHistoryAdapter
from imio.history.adapters import ImioRevisionHistoryAdapter


class TestingImioWfHistoryAdapter(ImioWfHistoryAdapter):

    def mayViewComment(self, event):
        """See docstring in interfaces.py."""
        if event['action'] == 'publish':
            return False


class TestingImioRevisionHistoryAdapter(ImioRevisionHistoryAdapter):

    def mayViewRevision(self, event):
        """See docstring in interfaces.py."""
        return False
