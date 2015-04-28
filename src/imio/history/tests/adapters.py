from imio.history.adapters import ImioWfHistoryAdapter


class TestingImioWfHistoryAdapter(ImioWfHistoryAdapter):

    def mayViewComment(self, event):
        """See docstring in interfaces.py."""
        if event['action'] == 'publish':
            return False
