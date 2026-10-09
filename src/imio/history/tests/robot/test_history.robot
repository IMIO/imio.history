*** Settings ***
Documentation  History of a document opened from the byline. Version-independent:
...            Plone selectors are in ui_plone*.robot.
Resource  imio_history.robot
Test Setup  Open a manager browser
Test Teardown  Close all browsers


*** Test Cases ***
The History link opens the history of a published document
    Create a document
    Change the state with a comment  ${DOC_URL}  publish  Published after review
    Open the history
    The history contains the event  ${PUBLISH}  ${MANAGER}  Published after review

The History link is highlighted when the last event has a comment
    ${uid}=  Create a document
    Open the document
    The history link is not highlighted
    Change the state with a comment  ${DOC_URL}  publish  Published after review
    Open the document
    The history link is highlighted
    Fire transition  ${uid}  retract
    Open the document
    The history link is not highlighted

The history of a versionable document shows its revisions
    Create a document
    Edit the title  ${DOC_URL}  My edited document
    Open the history
    The history shows the revision  0

A reviewer without the modify permission opens the history from the History link
    Create a document
    Change the state with a comment  ${DOC_URL}  publish  Published after review
    Create user  ${REVIEWER}  Reviewer  password=${REVIEWER_PASSWORD}
    Log in with the login form  ${REVIEWER}  ${REVIEWER_PASSWORD}
    Open the history
    The history contains the event  ${PUBLISH}  ${MANAGER}  Published after review
