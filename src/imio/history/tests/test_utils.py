# -*- coding: utf-8 -*-

from DateTime import DateTime
from imio import history as imio_history
from imio.history.interfaces import IImioHistory
from imio.history.testing import IntegrationTestCase
from imio.history.utils import add_event_to_history
from imio.history.utils import add_event_to_wf_history
from imio.history.utils import get_all_history_attr
from imio.history.utils import get_event_by_time
from imio.history.utils import getLastAction
from imio.history.utils import getLastWFAction
from imio.history.utils import getPreviousEvent
from plone import api
from plone.memoize.instance import Memojito
from Products.Five import zcml
from zope.component import getAdapter


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
        # clean memoize
        getattr(adapter, Memojito.propname).clear()
        history = adapter.getHistory()
        lastEvent = history[-1]
        self.assertEqual(lastEvent['action'], 'publish')
        self.assertEqual(getPreviousEvent(doc, lastEvent), firstEvent)

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
        adapter = getAdapter(doc, IImioHistory, 'workflow')
        self.assertEqual(getLastAction(adapter)['action'], 'publish')
        # same as getting action with that name
        publish_action = getLastAction(adapter, action='publish')
        self.assertEqual(publish_action['action'], 'publish')
        self.assertEqual(publish_action['comments'], 'First publication comment')

        # publish again, check that we correctly get last action
        api.content.transition(doc, 'retract')
        api.content.transition(doc, 'publish', comment='Second publication comment')
        # clean memoize
        getattr(adapter, Memojito.propname).clear()
        publish_action = getLastAction(adapter, action='publish')
        self.assertEqual(publish_action['action'], 'publish')
        self.assertEqual(publish_action['comments'], 'Second publication comment')

        # the creation event is stored with a None action
        self.assertEqual(getLastAction(adapter, action=None)['review_state'], 'private')

        # if action not found, None is returned
        self.assertIsNone(getLastAction(adapter, action='unknown_action'))

    def test_getLastAction_history_empty(self):
        """Does not breaks and returns None if history empty."""
        adapter = getAdapter(self.portal.folder, IImioHistory, 'revision')
        self.assertIsNone(getLastAction(adapter))

    def test_getLastAction_checkMayView(self):
        """Check checkMayViewEvent/checkMayViewComment, default implementation
           returns True."""
        doc = api.content.create(type='Document',
                                 id='doc',
                                 container=self.portal)
        # publish the doc so we have an new event in the workflow_history
        api.content.transition(doc, 'publish', comment='First publication comment')
        adapter = getAdapter(doc, IImioHistory, 'workflow')
        self.assertEqual(getLastAction(
            adapter, checkMayViewEvent=False, checkMayViewComment=False)['action'],
            'publish')
        self.assertEqual(getLastAction(
            adapter, checkMayViewEvent=True, checkMayViewComment=True)['action'],
            'publish')
        # enable testing-adapter.zcml, the 'publish' actions will
        # not be viewable anymore, as well as revisions
        zcml.load_config('testing-adapter.zcml', imio_history)
        self.request.set('hide_wf_history_event', True)
        self.request.set('hide_wf_history_comment', True)
        adapter = getAdapter(doc, IImioHistory, 'workflow')
        # checkMayViewEvent=False, checkMayViewComment=False
        res = getLastAction(adapter, checkMayViewEvent=False, checkMayViewComment=False)
        self.assertEqual(res['action'], 'publish')
        self.assertEqual(res['comments'], 'First publication comment')
        # checkMayViewEvent=True, checkMayViewComment=True
        self.assertIsNone(getLastAction(adapter, checkMayViewEvent=True, checkMayViewComment=True))
        # checkMayViewEvent=False, checkMayViewComment=True
        res = getLastAction(adapter, checkMayViewEvent=False, checkMayViewComment=True)
        self.assertEqual(res['action'], 'publish')
        self.assertEqual(res['comments'], adapter.comment_not_viewable_value)

    def test_getLastWFAction(self):
        """Test the utils.getLastWFAction method.
           It should return the action passed in parameter for the workflow_history.
           It is a shortcut using utils.getLastAction."""
        doc = api.content.create(type='Document',
                                 id='doc',
                                 container=self.portal)
        # 'before_last' action is None
        self.assertIsNone(getLastWFAction(doc, transition='before_last'))
        # publish the doc so we have an new event in the workflow_history
        api.content.transition(doc, 'publish', comment='Publication comment')
        self.assertEqual(getLastWFAction(doc)['action'], 'publish')
        # same as getting action with that name
        publish_action = getLastWFAction(doc, transition='publish')
        self.assertEqual(publish_action['action'], 'publish')
        self.assertEqual(publish_action['comments'], 'Publication comment')
        self.assertEqual(getLastWFAction(doc, transition='before_last')['review_state'], 'private')

    def test_getLastWFAction_ignore_previous_event_actions(self):
        """Test utils.getLastWFAction with ignore_previous_event_actions."""
        doc = api.content.create(type='Document',
                                 id='doc',
                                 container=self.portal)
        # we are going to:
        # publish, retract, submit, publish
        # then get the last publish ignoring previous "submit"
        api.content.transition(doc, 'publish', comment='Publication comment')
        api.content.transition(doc, 'retract', comment='Retract comment')
        api.content.transition(doc, 'submit', comment='Submit comment')
        api.content.transition(doc, 'publish', comment='Publication2 comment')
        action = getLastWFAction(doc, 'publish')
        action_with_ignored_previous = getLastWFAction(
            doc, 'publish', ignore_previous_event_actions=['submit'])
        self.assertNotEqual(action['time'], action_with_ignored_previous['time'])
        self.assertEqual(action['action'], 'publish')
        self.assertEqual(action_with_ignored_previous['action'], 'publish')
        self.assertEqual(action['comments'], 'Publication2 comment')
        self.assertEqual(action_with_ignored_previous['comments'], 'Publication comment')

    def test_add_event_to_history(self):
        """Add an event to an history following an action."""
        folder = self.portal.folder
        # if history attr does not exist, it is created
        DUMMY_HISTORY_ATTR = 'dummy_history'
        self.assertFalse(hasattr(folder, DUMMY_HISTORY_ATTR))

        # action1 with default values
        add_event_to_history(folder, DUMMY_HISTORY_ATTR, 'action1')
        added_action1 = getattr(folder, DUMMY_HISTORY_ATTR)[0]
        self.assertEqual(added_action1['action'], 'action1')
        # current user id in actor
        self.assertEqual(added_action1['actor'], 'test_user_1_')
        self.assertEqual(added_action1['actor'], api.user.get_current().getId())
        self.assertEqual(added_action1['comments'], '')
        self.assertTrue(isinstance(added_action1['time'], DateTime))

        # action2 with parameters
        new_user = api.user.create(username='dummy_user', email='dummy@user.org')
        add_event_to_history(folder,
                             DUMMY_HISTORY_ATTR,
                             'action2',
                             actor=new_user,
                             time=DateTime('2018/01/12'),
                             comments=u'My comments',
                             extra_infos={'dummy_info1': u'Information 1',
                                          'dummy_info2': u'Information 2'})
        added_action2 = getattr(folder, DUMMY_HISTORY_ATTR)[1]
        self.assertEqual(added_action2['action'], 'action2')
        self.assertEqual(added_action2['actor'], new_user.getId())
        self.assertEqual(added_action2['comments'], u'My comments')
        self.assertEqual(added_action2['time'], DateTime('2018/01/12'))
        # extra infos
        self.assertEqual(added_action2['dummy_info1'], u'Information 1')
        self.assertEqual(added_action2['dummy_info2'], u'Information 2')

    def test_get_all_history_attr(self):
        """Get every coccurence of a given attr_name in a history."""
        doc = api.content.create(type='Document',
                                 id='doc',
                                 container=self.portal)
        api.content.transition(doc, 'publish', comment='Publication comment')
        api.content.transition(doc, 'retract')
        self.assertEqual(get_all_history_attr(doc), [None, 'publish', 'retract'])
        self.assertEqual(get_all_history_attr(doc, attr_name='review_state'),
                         ['private', 'published', 'private'])
        self.assertEqual(get_all_history_attr(doc, attr_name='actor'),
                         ['test_user_1_', 'test_user_1_', 'test_user_1_'])
        self.assertEqual(get_all_history_attr(doc, attr_name='comments'),
                         ['', 'Publication comment', ''])

    def test_get_event_by_time(self):
        doc = api.content.create(type='Document',
                                 id='doc',
                                 container=self.portal)
        api.content.transition(doc, 'publish', comment='Publication comment')
        api.content.transition(doc, 'retract')
        float_event_time = float(doc.workflow_history['simple_publication_workflow'][-1]['time'])
        self.assertEqual(get_event_by_time(doc, 'workflow', float_event_time)['action'], 'retract')
        self.assertIsNone(get_event_by_time(doc, 'workflow', 0))

    def test_add_event_to_wf_history(self):
        doc = api.content.create(type='Document',
                                 id='doc',
                                 container=self.portal)
        add_event_to_wf_history(doc, action="test", comments="Test")
        self.assertEqual(doc.workflow_history['simple_publication_workflow'][-1]['action'], "test")
        # insert at index 1
        add_event_to_wf_history(doc, action="test2", comments="Test2", insert_index=1)
        self.assertEqual(doc.workflow_history['simple_publication_workflow'][-1]['action'], "test")
        self.assertEqual(doc.workflow_history['simple_publication_workflow'][-2]['action'], "test2")
