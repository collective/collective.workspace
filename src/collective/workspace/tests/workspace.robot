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
    Set window size  1200  900

Open Toolbar Menu
    [Arguments]  ${elementId}
    Element Should Be Visible  css=#${elementId} a
    Element Should Not Be Visible  css=#${elementId} ul a
    Click link  css=#${elementId} a
    Wait until keyword succeeds  1  5  Element Should Be Visible  css=#${elementId} ul a

a test workspace
    Log in as site owner
    Go to  ${PLONE_URL}
#   Open Add New Menu  # Broken because still no Plone 5 kw in p.a.rf
    Open Toolbar Menu  plone-contentmenu-factories
    Click link  css=.contenttype-workspace
    Input text  form-widgets-IBasic-title  Test Workspace
    Click button  id=form-buttons-save

the test user is added to the roster
	Click link  css=#contentview-team-roster a
	Click Overlay Link  workspace-add-user
	Input text  css=#formfield-form-widgets-user input  test
	Wait until page contains  test_user_1_
	Click element  jquery=li:contains('test_user_1_')
	Press key  css=#formfield-form-widgets-position input  \\13
#   Click button  id=form-buttons-save  # Broken on phantomjs because of plone-modal DOM manipulations

the test user appears in the roster
	Wait until page contains element  css=a[href$="edit-roster/test_user_1_"]

the test user can view the workspace
	Log in as test user
	Go to  http://localhost:55001/plone/test-workspace
	Page should contain  Roster
