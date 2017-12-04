# -*- coding: utf-8 -*-

from zope.component import getAdapter
from imio.history.interfaces import IImioHistory


def getPreviousEvent(obj, event, checkMayView=True):
    '''Returns the previous event found in the history for the given p_event
       on p_obj if p_event is found.  p_checkMayView is passed to IImioHistory.getHistory
       and will enable/disable event's comments viewability check.'''

    adapter = getAdapter(obj, IImioHistory, 'workflow')
    history = adapter.getHistory(checkMayView=checkMayView)
    if event in history and history.index(event) > 0:
        return history[history.index(event) - 1]


def getLastAction(obj, action='last', history_name='workflow', checkMayView=False):
    '''Returns, from the p_history_name of p_obj, the last occurence of p_event.
       Default p_action is 'last' because we also want to be able to get
       an action that is 'None' in a particular p_history_name.'''

    adapter = getAdapter(obj, IImioHistory, history_name)
    history = adapter.getHistory(checkMayView=checkMayView)

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
