# -*- coding: utf-8 -*-

from DateTime import DateTime
from imio.helpers.cache import get_current_user_id
from imio.history.interfaces import IImioHistory
from persistent.list import PersistentList
from plone import api
from Products.CMFPlone.utils import base_hasattr
from zope.component import getAdapter


def _check_may_view(event, adapter, checkMayViewEvent=False, checkMayViewComment=False):
    if event is not None:
        if checkMayViewEvent:
            if not adapter.mayViewEvent(event):
                event = None
        if checkMayViewComment and event is not None:
            if not adapter.mayViewComment(event):
                event['comments'] = adapter.comment_not_viewable_value
    return event


def getPreviousEvent(obj, event, checkMayViewEvent=False, checkMayViewComment=False):
    '''Returns the previous event found in the history for the given p_event
       on p_obj if p_event is found.  p_checkMayView is passed to IImioHistory.getHistory
       and will enable/disable event's comments viewability check.'''

    adapter = getAdapter(obj, IImioHistory, 'workflow')
    # for performance, checkMayViewEvent and checkMayViewComment only on found event
    history = adapter.getHistory(
        checkMayViewEvent=False, checkMayViewComment=False)
    res = None
    if event in history and history.index(event) > 0:
        res = history[history.index(event) - 1]

    return _check_may_view(res, adapter, checkMayViewEvent, checkMayViewComment)


def getLastAction(adapter,
                  action='last',
                  ignore_previous_event_actions=[],
                  checkMayViewEvent=False,
                  checkMayViewComment=False):
    '''Returns, from the p_history_name of p_adapter, the last occurence of p_action.
       Default p_action is 'last' because we also want to be able to get
       an action that is 'None' in a particular p_history_name.'''

    # for performance, checkMayViewEvent and checkMayViewComment only on found event
    history = adapter.getHistory(
        checkMayViewEvent=False, checkMayViewComment=False)

    res = None
    if action == 'last':
        # do not break if history is empty
        res = history and history[-1] or None
    elif action == 'before_last':
        # do not break if history empty or only contains one single event
        res = len(history) > 1 and history[-2] or None
    else:
        i = len(history) - 1
        while i >= 0:
            event = history[i]
            if isinstance(action, basestring):
                condition = event['action'] == action
            elif action is None:
                condition = event['action'] is None
            else:
                condition = event['action'] in action
            if condition and \
                    (not ignore_previous_event_actions or
                     history[i - 1]['action'] not in ignore_previous_event_actions):
                res = event
                break
            i -= 1

    return _check_may_view(res, adapter, checkMayViewEvent, checkMayViewComment)


def getLastWFAction(obj,
                    transition='last',
                    ignore_previous_event_actions=[],
                    checkMayViewEvent=False,
                    checkMayViewComment=False):
    '''Helper to get last p_transition workflow_history event.
       By default, security checks are not done (checkMayViewEvent=False, checkMayViewComment=False).'''
    adapter = getAdapter(obj, IImioHistory, 'workflow')
    last_wf_action = getLastAction(
        adapter,
        action=transition,
        ignore_previous_event_actions=ignore_previous_event_actions,
        checkMayViewEvent=checkMayViewEvent,
        checkMayViewComment=checkMayViewComment)
    return last_wf_action


def get_all_history_attr(obj,
                         attr_name='action',
                         history_name='workflow',
                         checkMayViewEvent=False,
                         checkMayViewComment=False):
    '''Return a list of every p_attr_name for p_history_name of p_obj.'''
    adapter = getAdapter(obj, IImioHistory, history_name)
    res = [event[attr_name] for event in adapter.getHistory(checkMayViewEvent, checkMayViewComment)]
    return res


def add_event_to_history(obj, history_attr, action, actor=None, time=None, comments=u'', extra_infos={}):
    '''This is an helper method to add an entry to an history.'''
    if not base_hasattr(obj, history_attr):
        setattr(obj, history_attr, PersistentList())
    history_data = {'action': action,
                    'actor': actor and actor.getId() or api.user.get_current().getId(),
                    'time': time or DateTime(),
                    'comments': comments}
    history_data.update(extra_infos)
    getattr(obj, history_attr).append(history_data.copy())


def add_event_to_wf_history(obj, action, actor=None, comments=u'', insert_index=None):
    wfTool = api.portal.get_tool('portal_workflow')
    wfs = wfTool.getWorkflowsFor(obj)
    if not wfs:
        return
    wf = wfs[0]
    wfName = wf.id
    # get review_state from last event if any
    events = list(obj.workflow_history[wfName]) or []
    if events:
        previous_event = events[-1]
        review_state_id = previous_event['review_state']
    else:
        # use initial_state
        review_state_id = wf.initial_state
    # action comments must be translated in the imio.history domain
    new_event = {}
    new_event['comments'] = comments or ''
    # action_name must be translated in the plone domain
    new_event['action'] = action
    new_event['actor'] = actor or get_current_user_id(obj.REQUEST)
    # if an insert_index is defined, use same 'time' as previous as
    # events are sorted on 'time' and just add 1 millisecond
    if insert_index is not None:
        new_event['time'] = events[insert_index]['time'] + 0.000000001
        new_event['review_state'] = events[insert_index]['review_state']
        events.insert(insert_index, new_event)
    else:
        new_event['time'] = DateTime()
        new_event['review_state'] = review_state_id
        events.insert(len(events), new_event)
    obj.workflow_history[wfName] = events


def get_event_by_time(obj, history_name, float_event_time):
    """Return event of an history corresponding to the given p_float_event_time "time"."""
    adapter = getAdapter(obj, IImioHistory, history_name)
    for event in adapter.get_history_data():
        if float(event['time']) == float_event_time:
            return event
