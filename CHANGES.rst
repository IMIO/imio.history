Changelog
=========

1.3 (unreleased)
----------------

- Do not reverse workflow_history in ImioHistoryAdapter.getHistory 
  as it is for display purpose, do this in the IHContentHistoryView.getHistory
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
