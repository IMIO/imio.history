*** Settings ***
Documentation  imio.history keywords, built on the ui_plone${PLONE_MAJOR}.robot keywords.
...            Robot Framework 3.0 syntax (shared with the Plone 4.3 environment).
Resource  ui_plone${PLONE_MAJOR}.robot


*** Variables ***
${DOC_URL}  ${PLONE_URL}/doc
# autologin user (Enable autologin as  Manager), actor of the events
${MANAGER}  Manager
${REVIEWER}  reviewer
${REVIEWER_PASSWORD}  reviewer-secret
# title of the publish transition of simple_publication_workflow
${PUBLISH}  Reviewer publishes content
${HIGHLIGHTED_STYLE}  rgb(255, 0, 0) 700
# table of @@contenthistory (id history-list on Plone 6 only)
${HISTORY_TABLE}  //table[thead/tr/th[@class="history-action"]]


*** Keywords ***
Open a manager browser
    Open test browser
    Enable autologin as  Manager

Create a document
    [Documentation]  Private Document "doc", returns its UID
    ${uid}=  Create content  type=Document  id=doc  title=My document
    [Return]  ${uid}

Open the document
    Go to  ${DOC_URL}

Open the history
    [Documentation]  With the History link of the byline
    Open the document
    Click link  css=#content-history a
    The history is shown

The history contains the event
    [Arguments]  ${action}  ${actor}  ${comment}
    Page should contain element
    ...  xpath=${HISTORY_TABLE}//tr[td[1][normalize-space()="${action}"] and td[2][normalize-space()="${actor}"] and td[4]/p[normalize-space()="${comment}"]]

The history shows the revision
    [Documentation]  Row of the revision: View link and "Revert to this revision" button
    [Arguments]  ${version_id}
    ${row}=  Set variable  ${HISTORY_TABLE}//tr[td[1][normalize-space()="Edited"] and .//input[@name="version_id" and @value="${version_id}"]]
    Page should contain element
    ...  xpath=${row}//a[normalize-space()="View" and contains(@href, "versions_history_form?version_id=${version_id}")]
    Page should contain element
    ...  xpath=${row}//form[contains(@action, "/revertversion")]//*[@value="Revert to this revision" or normalize-space()="Revert to this revision"]

History link style
    [Documentation]  Computed color and font weight of the History link
    ${style}=  Execute javascript
    ...  var style = window.getComputedStyle(document.querySelector('#content-history a')); return style.color + ' ' + style.fontWeight;
    [Return]  ${style}

The history link is highlighted
    Page should contain element  css=#content-history.highlight-history-link
    ${style}=  History link style
    Should be equal  ${style}  ${HIGHLIGHTED_STYLE}

The history link is not highlighted
    Page should contain element  css=#content-history a
    Page should not contain element  css=#content-history.highlight-history-link
    ${style}=  History link style
    Should not be equal  ${style}  ${HIGHLIGHTED_STYLE}
