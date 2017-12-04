from DateTime import DateTime

from zope.component import getAdapter
from zope.component import ComponentLookupError
from plone import api

from imio.history.interfaces import IImioHistory
from imio.history.testing import IntegrationTestCase
from imio.history.utils import getLastAction
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
        api.content.transition(doc, 'publish', comment='My comment')
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

    def test_getLastAction(self):
        """Test the utils.getLastAction method.
           It should return the action passed in parameter for the given history name."""
        doc = api.content.create(type='Document',
                                 id='doc',
                                 container=self.portal)
        # publish the doc so we have an new event in the workflow_history
        api.content.transition(doc, 'publish', comment='First publication comment')
        self.assertEqual(getLastAction(doc)['action'], 'publish')
        # same as getting action with that name
        publish_action = getLastAction(doc, action='publish')
        self.assertEqual(publish_action['action'], 'publish')
        self.assertEqual(publish_action['comments'], 'First publication comment')

        # publish again, check that we correctly get last action
        api.content.transition(doc, 'retract')
        api.content.transition(doc, 'publish', comment='Second publication comment')
        publish_action = getLastAction(doc, action='publish')
        self.assertEqual(publish_action['action'], 'publish')
        self.assertEqual(publish_action['comments'], 'Second publication comment')

        # the creation event is stored with a None action
        self.assertEqual(getLastAction(doc, action=None)['review_state'], 'private')

        # if action not found, None is returned
        self.assertIsNone(getLastAction(doc, action='unknown_action'))

    def test_getLastAction_unknown_history(self):
        """Breaks if unknown history."""
        self.assertRaises(
            ComponentLookupError,
            getLastAction, self.portal.folder, history_name='unknown_history')

    def test_getLastAction_history_empty(self):
        """Does not breaks and returns None if history empty."""
        self.assertIsNone(getLastAction(self.portal.folder, history_name='revision'))
