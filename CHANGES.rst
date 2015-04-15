Changelog
=========

1.4 (unreleased)
----------------

- Nothing changed yet.


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
