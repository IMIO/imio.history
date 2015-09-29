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
