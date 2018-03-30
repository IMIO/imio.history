.. image:: https://travis-ci.org/IMIO/imio.history.svg
    :target: https://travis-ci.org/IMIO/imio.history

.. image:: https://coveralls.io/repos/IMIO/imio.history/badge.svg
  :target: https://coveralls.io/r/IMIO/imio.history


imio.history
============

Manage object history using a table and highlight history link when necessary

The goal is to be able to manage several histories for various needs on a content and display it together, merged in the same view.

Adapters implementing the `IImioHistory` interface
--------------------------------------------------

To do this, we must ensure that the histories use same structure.  We base the work on the `workflow_history`, though a custom history may have additional keys if necessary.

The workflow_history could looks like :

.. code-block:: python

    {'my_custom_workflow': (
        {'action': None, 'review_state': 'private', 'actor': 'user_id1',
        'comments': '', 'time': DateTime('2018/03/27 09:51:55.303708 GMT+2')},
        {'action': 'publish', 'review_state': 'published', 
        'comments': '', 'actor': 'user_id1', 'time': DateTime('2018/03/29 15:35:24.646745 GMT+2')},
        {'action': 'retract', 'review_state': 'private',
        'comments': 'My comments', 'actor': 'admin', 'time': DateTime('2018/03/29 15:35:27.246169 GMT+2')})}

Histories are made available thru a named adapter that implements the `IImioHistory` interface.

By default, adapters are provided for the `workflow_history` (`ImioWfHistoryAdapter`) and revisions history (`ImioRevisionHistoryAdapter`).

The `@@historyview`
-------------------

The `@@historyview` will display the histories as a table with each information in a column : action, author, date/time, comments.

You define in the `histories_to_handle` attribute of the view, what histories (named adapters) it should display.

Every histories are sorted together on the `time` key as it uses the same structure.
