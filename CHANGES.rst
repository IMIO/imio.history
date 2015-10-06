Changelog
=========

1.8 (unreleased)
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
