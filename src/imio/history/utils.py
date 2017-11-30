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


def getLastAction(obj, action=None, history_name='workflow', checkMayView=False):
    '''Returns, from the p_history_name of p_obj, the last occurence of p_event.'''

    adapter = getAdapter(obj, IImioHistory, history_name)
    history = adapter.getHistory(checkMayView=checkMayView)

    if not action:
        return history[-1]

    i = len(history) - 1
    while i >= 0:
        event = history[i]
        if isinstance(action, basestring):
            condition = event['action'] == action
        else:
            condition = event['action'] in action
        if condition:
            return event
        i -= 1
