from DateTime import DateTime

from zope.component import getAdapter
from plone import api

from imio.history.interfaces import IImioHistory
from imio.history.testing import IntegrationTestCase
from imio.history.utils import getPreviousEvent


class TestUtils(IntegrationTestCase):

    def test_getPreviousEvent(self):
        """Test the getPreviousEvent method.
           It should return the previous event for a given event if it exists."""
        doc = api.content.create(type='Document',
                                 id='doc',
                                 container=self.portal)
        adapter = getAdapter(doc, IImioHistory, 'workflow')
        history = adapter.getHistory()
        firstEvent = history[0]
        # this is the 'creation' event
        self.assertTrue(firstEvent['action'] is None)
        self.assertTrue(getPreviousEvent(doc, firstEvent) is None)

        # now publish the doc so we have an new event in the workflow_history
        self.wft.doActionFor(doc, 'publish', comment='My comment')
        history = adapter.getHistory()
        lastEvent = history[-1]
        self.assertTrue(lastEvent['action'] == 'publish')
        self.assertTrue(getPreviousEvent(doc, lastEvent) == firstEvent)

        # if the event is not found, None is returned
        wrongEvent = {'action': 'wrong',
                      'review_state': 'wrong',
                      'comments': 'My wrong comment',
                      'actor': 'wrong',
                      'time': DateTime('2015/01/01 13:30:0.0 GMT+2')}
        self.assertTrue(getPreviousEvent(doc, wrongEvent) is None)
