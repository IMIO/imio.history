from imio.history.adapters import ImioWfHistoryAdapter
from imio.history.adapters import ImioRevisionHistoryAdapter


class TestingImioWfHistoryAdapter(ImioWfHistoryAdapter):

    def mayViewEvent(self, event):
        """See docstring in interfaces.py."""
        if event['action'] == 'publish':
            return False
        return True

    def mayViewComment(self, event):
        """See docstring in interfaces.py."""
        if event['action'] == 'publish':
            return False
        return True


class TestingImioRevisionHistoryAdapter(ImioRevisionHistoryAdapter):

    def mayViewEvent(self, event):
        """See docstring in interfaces.py."""
        return False

    def mayViewComment(self, event):
        """See docstring in interfaces.py."""
        return False
