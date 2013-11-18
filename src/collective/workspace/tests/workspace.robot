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
    Open browser  http://localhost:55001/plone/  browser=${BROWSER}

a test workspace
    Log in as site owner
    Go to  ${PLONE_URL}
    Open Add New Menu
    Click link  css=.contenttype-workspace
    Input text  form-widgets-IBasic-title  Test Workspace
    Click button  Save

the test user is added to the roster
	Click link  Roster
	Click Overlay Link  workspace-add-user
	Input text  form-widgets-user-widgets-query  test
	Wait until page contains  test_user_1_
	Click element  jquery=li:contains('test_user_1_')
	Click button  Save

the test user appears in the roster
	Page should contain element  css=a[href$="edit-roster/test_user_1_"]	

the test user can view the workspace
	Log in as test user
	Go to  http://localhost:55001/plone/test-workspace
	Page should contain  Roster
