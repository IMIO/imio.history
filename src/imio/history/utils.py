# -*- coding: utf-8 -*-

from DateTime import DateTime
from imio.history.interfaces import IImioHistory
from persistent.list import PersistentList
from plone import api
from Products.CMFPlone.utils import base_hasattr
from zope.component import getAdapter


def getPreviousEvent(obj, event, checkMayViewEvent=True, checkMayViewComment=True):
    '''Returns the previous event found in the history for the given p_event
       on p_obj if p_event is found.  p_checkMayView is passed to IImioHistory.getHistory
       and will enable/disable event's comments viewability check.'''

    adapter = getAdapter(obj, IImioHistory, 'workflow')
    history = adapter.getHistory(
        checkMayViewEvent=checkMayViewEvent, checkMayViewComment=checkMayViewComment)
    if event in history and history.index(event) > 0:
        return history[history.index(event) - 1]


def getLastAction(adapter, action='last', checkMayViewEvent=True, checkMayViewComment=True):
    '''Returns, from the p_history_name of p_obj, the last occurence of p_event.
       Default p_action is 'last' because we also want to be able to get
       an action that is 'None' in a particular p_history_name.'''

    history = adapter.getHistory(
        checkMayViewEvent=checkMayViewEvent, checkMayViewComment=checkMayViewComment)

    if action == 'last':
        # do not break if history is empty
        return history and history[-1] or None

    i = len(history) - 1
    while i >= 0:
        event = history[i]
        if isinstance(action, basestring):
            condition = event['action'] == action
        elif action is None:
            condition = event['action'] is None
        else:
            condition = event['action'] in action
        if condition:
            return event
        i -= 1


def getLastWFAction(obj, transition='last'):
    '''Helper to get last p_transition workflow_history event.'''
    adapter = getAdapter(obj, IImioHistory, 'workflow')
    last_wf_action = getLastAction(adapter, action=transition)
    return last_wf_action


def add_event_to_history(obj, history_attr, action, actor=None, time=None, comments=u'', extra_infos={}):
    """This is an helper method to add an entry to an history."""
    if not base_hasattr(obj, history_attr):
        setattr(obj, history_attr, PersistentList())
    history_data = {'action': action,
                    'actor': actor and actor.getId() or api.user.get_current().getId(),
                    'time': time or DateTime(),
                    'comments': comments}
    history_data.update(extra_infos)
    getattr(obj, history_attr).append(history_data.copy())
