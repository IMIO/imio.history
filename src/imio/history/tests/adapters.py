from imio.history.adapters import ImioHistoryAdapter


class TestingImioHistoryAdapter(ImioHistoryAdapter):

    def mayViewComment(self, event):
        """See docstring in interfaces.py."""
        if event['action'] == 'publish':
            return False
