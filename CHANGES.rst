Changelog
=========

1.33 (2023-12-11)
-----------------

- Added `utils.add_event_to_wf_history` to insert an event
  to the `workflow_history` of an element.
  [gbastien]

1.32 (2023-11-27)
-----------------

- In `IHDocumentBylineViewlet`, do not display creator if `show_history`
  is `False` as creator is part of the history.
  [gbastien]
- In `@@historyview`, display a `@@header` view under `History` title that will
  by default display the `prettylink` of the context, useful when displaying
  history in a popup from a dashboard containing plenty of elements.
  Added direct dependency on `imio.prettylink`.
  [gbastien]

1.31 (2023-10-27)
-----------------

- Added parameter `ignore_previous_event_actions=[]` to `utils.getLastAction`,
  this way when finding the last action in a history, it will check previous
  event action and continue if it is an action to ignore.
  [gbastien]

1.30 (2023-09-21)
-----------------

- Added `utils.get_event_by_time` that will return an history event based
  on a given float event time.
  [gbastien]
- Formalized use of `EventPreviewView.may_view_historized_data`.
  [gbastien]

1.29 (2023-06-27)
-----------------

- Make `IHContentHistoryView.renderComments` more robust by passing original
  `mimetype='text/plain'` to avoid `portal_transforms` detecting it automatically
  that can lead to wrong detection.
  [gbastien]

1.28 (2023-02-27)
-----------------

- Added possibility to display an event preview under the comment
  in the `@@contenthistory` view.
  [gbastien]
- Make the `highlight_last_comment` functionnality generic, it was only used
  with WF history but now any history may be set `highlight_last_comment=True`.
  [gbastien]

1.27 (2022-06-14)
-----------------

- Added `safe_utils.py` that will only include safe utils.
  [gbastien]

1.26 (2022-03-08)
-----------------

- Fixed display of actor fullname in `@@historyview`.
  [gbastien]

1.25 (2022-03-07)
-----------------

- Optimized `@@contenthistory` view.
  [gbastien]

1.24 (2022-02-25)
-----------------

- In `content_history` template, only fix date column width,
  for other columns, let the browser optimize it.
  [gbastien]

1.23 (2021-04-21)
-----------------

- Add Transifex.net service integration to manage the translation process.
  [macagua]
- Add Spanish translation
  [macagua]

1.22 (2021-03-04)
-----------------

- Changed default to `False` for parameters `checkMayViewEvent=False` and
  `checkMayViewComment=False` of `utils.getLastAction`, this way, we get last
  action even if current user may not, and it is quicker.
  This fix a performance issue in `ImioWfHistoryAdapter.historyLastEventHasComments`
  when called several times.
  [gbastien]
- In `utils.getLastAction`, parameter `action` may be `before_last` and will
  return the before last action if it exists.
  [gbastien]

1.21 (2020-10-26)
-----------------

- Added helper `utils.get_all_history_attr` to get every occurence of a given
  `attr_name` in a `history`. This will return every `review_state` from the
  `workflow` history for example.
  [gbastien]

1.20 (2020-10-01)
-----------------

- Added parameters `checkMayViewEvent=False` and `checkMayViewComment=False` to
  `utils.getLastWFAction`, this way, we get last WF action even if current user
  may not, and it is quicker.
  [gbastien]

1.19 (2019-10-01)
-----------------

- Allow access to module `utils` from restricted python (TAL expression).
  [gbastien]

1.18 (2019-01-11)
-----------------

- As `ImioWfHistoryAdapter.ignorableHistoryComments` should return a list of
  unicode, we force unicode comparison in
  `ImioWfHistoryAdapter.historyLastEventHasComments`, this way we avoid warning
  in Zope log.
  [gbastien]
- `isort` on imports.
  [gbastien]
- Added helper `utils.getLastWFAction` that is actually a shortcut to
  `utils.getLastAction` using the `IImioHistory` 'workflow' adapter.
  [gbastien]

1.17 (2018-03-19)
-----------------

- Factorize `show_history` functionnality.  The method is now defined on the
  `IHContentHistoryView` and is used by
  `IHDocumentBylineViewlet.show_history` and the `@@historyview`.
  This way, we make sure that if the link is not shown on the viewlet, the
  history is not shown in the `@@historyview` if user enter the view name
  manually in the browser.
  [gbastien]

1.16 (2018-02-22)
-----------------

- Use `@memoize` on `BaseImioHistoryAdapter.get_history_data` and
  `BaseImioHistoryAdapter.getHistory` to avoid recomputing it if adapter did
  not changed.  This is useful for the `highlight_history_link` functionnality.
  [gbastien]
- `utils.getLastAction` now receives an `IImioHistory` adapter as first
  argument instead an obj and an adapter name.
  [gbastien]

1.15 (2018-02-09)
-----------------

- Added attribute `ImioWfHistoryAdapter.include_previous_review_state`,
  `False` by default, if set to `True`, the returned history will include
  `previous_review_state`.
  [gbastien]

1.14 (2018-01-23)
-----------------

- Refactored code so it is easy to handle no histories.
  [gbastien]
- Do not fail to call workflow_history specific methods if obj has no workflow.
  [gbastien]
- `IHContentHistoryView.renderComments` now receives the entire event as
  parameter not just the comment so it pass the different values of the event as
  mapping to the translate method so it is useable in translated comment.
  [gbastien]
- Added `IHContentHistoryView.renderCustomJS` to be able to inject custom JS
  when loading the `@@historyview`, especially because it is loaded as an
  overlay.
  [gbastien]
- Added helper `utils.add_event_to_history` that adds an event to an history
  respecting minimum required data.
  [gbastien]
- Added the `BaseImioHistoryAdapter.mayViewEvent` method used when parameter
  `checkMayViewEvent=True`, it returns `True` by default but is made to be
  overrided, if returns False, the entire event is not displayed in the
  `@@historyview`.
  [gbastien]

1.13 (2017-12-07)
-----------------

- In `utils.getLastAction`, do not break if history is empty, added tests.
  [gbastien]

1.12 (2017-11-30)
-----------------

- Define a `BaseImioHistoryAdapter` to base new history adapter on.
  `checkMayView=True` is now a default parameter of `getHistory`.
  [gbastien]
- For now, specifically restrict histories displayed in the `@@historyview` to
  `workflow` and `revision`.
  [gbastien]
- Added method `utils.getLastAction` that returns the metadata of last action of
  a given name for a given history.
  [gbastien]

1.11 (2017-06-23)
-----------------

- Adapted History word highlighting ti display it bigger and underline it so
  it is even more viewable.
  [gbastien]

1.10 (2017-06-14)
-----------------

- In ImioWfHistoryAdapter.historyLastEventHasComments, call
  ImioWfHistoryAdapter.getHistory with parameter 'for_last_event=True' so
  getHistory knows that it queries only relevant last event and when overrided,
  the package overriding it may avoid heavy processing if relevant.
  [gbastien]
- Get rid of unittest2.
  [gbastien]

1.9 (2016-10-12)
----------------

- Do not break in IHContentHistoryView.getTransitionTitle if transitionName
  contains special characters.
  [gbastien]

1.8 (2015-10-06)
----------------

- Make sure comments is displayed correctly by using portal_transforms to
  turn it to 'text/html' before displaying it in the PageTemplate using
  'structure'.
  [gbastien]

1.7 (2015-09-28)
----------------

- Remove revision columns when unused.
  [DieKatze]
- In ImioRevisionHistoryAdapter.getHistory, take into account the
  'checkMayView' parameter by implementing a 'mayViewRevision' method so it
  is possible to restrict access to a specific revision if necessary
  [gbastien]

1.6 (2015-09-10)
----------------

- Added @@history-version-preview view that is called by default in the
  content_history but that renders nothing.  It is made to be registered for a
  relevant content_type so it is possible to display a preview of a versioned
  object directly in the history popup
  [gbastien]

1.5 (2015-07-14)
----------------

- Add revision history management.
  [cedricmessiant]

1.4 (2015-04-15)
----------------

- Added helper method 'utils.getPreviousEvent' that will receive an event
  as parameter and will return the previous event in the workflow_history
  if found
  [gbastien]

1.3 (2015-04-15)
----------------

- Do not reverse workflow_history in ImioHistoryAdapter.getHistory
  as it is for display purpose, do this in the IHContentHistoryView.getHistory
  [gbastien]
- Added parameter 'checkMayView' to ImioHistoryAdapter.getHistory to be able
  to enable/disable mayViewComment check while getting the workflow_history
  [gbastien]

1.2 (2015-04-01)
----------------

- Be defensive in getHistory, do not fail if no workflow used or
  if element has no workflow_history attribute
  [gbastien]

1.1 (2015-03-31)
----------------

- Register translations
  [gbastien]

1.0 (2015-03-30)
----------------

- Intial release
