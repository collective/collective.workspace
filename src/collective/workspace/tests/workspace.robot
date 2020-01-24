*** Settings ***

Resource  plone/app/robotframework/keywords.robot

Library  Selenium2Library  timeout=10  implicit_wait=0.5

Suite Setup  Start browser
Suite Teardown  Close All Browsers

*** Variables ***

${BROWSER} =  firefox

*** Test Cases ***

Scenario: Workspace member is listed in roster
	Given a test workspace
	When the test user is added to the roster
	Then the test user appears in the roster

Scenario: Workspace member gains access to workspace
    Given a test workspace
     When the test user is added to the roster
     Then the test user can view the workspace


*** Keywords ***

Start browser
    Open browser  ${START_URL}  browser=${BROWSER}

a test workspace
    Log in as site owner
    Go to  ${PLONE_URL}
    Open Add New Menu
    Click link  css=.contenttype-workspace
    Input text  form-widgets-IBasic-title  Test Workspace
    Click button  Save

the test user is added to the roster
	Click link  css=#contentview-team-roster a
	Click Overlay Link  workspace-add-user
    Wait Until Page Contains Element  css=#formfield-form-widgets-user input
    Click Element  css=#formfield-form-widgets-user input
    Wait Until Page Contains Element  jquery=.select2-result-label:contains("Test user")
    Click Element  jquery=.select2-result-label:contains("Test user")
    Click button  css=.pattern-modal-buttons #form-buttons-save

the test user appears in the roster
	Wait Until Page Contains Element  css=a[href$="edit-roster/test_user_1_"]

the test user can view the workspace
	Log in as test user
	Go to  ${START_URL}/test-workspace
	Page should contain  Roster
