.. image:: https://github.com/collective/collective.workspace/workflows/tests/badge.svg
    :target: https://github.com/collective/collective.workspace/actions?query=workflow%3Atests

collective.workspace
====================

Introduction
------------

collective.workspace package for providing 'membership' in specific areas of a Plone Site.

It allows you to grant people access to areas of content using a membership group rather than local roles for each user, and to delegate control over that group to people who don't have access to the site-wide user/group control panel.

collective.workspace provides a ``collective.workspace.team_workspace`` behavior that can be enabled for any Dexterity content type. When enabled, it adds a "Roster" tab which is where you can manage the team.

All the functionality takes place via an IWorkspace adapter, which can be overridden to specify:

* A list of groups, and the roles that each group should receive. These groups are created automatically via a PAS plugin, and automatically granted local roles using a borg.localrole adapter.
* The schema for which fields should be stored for each member in the roster. This includes checkboxes for the groups, to determine which groups the member is in.
* Action links for each row in the roster. The default is an "Edit" link which brings up a popup to edit the fields for that person's roster membership.
* Action buttons at the bottom of the roster which apply to the rows the user selects. An example of this could be a 'Send email' action, so a roster admin can easily email users in the roster.

Unlike similar previous packages (see slc.teamfolder and collective.local.*), collective.workspace supplies its own PAS groups plugin, instead of using standard Plone groups. This means that you can prevent Workspace-specific groups from appearing in the sitewide group control panel.

Some other features are:

* Membership in a roster is indexed, so you can search the catalog for items of portal_type X that have a particular user in their roster.
* Events are fired when roster memberships are added/modified/removed.

Basic Installation
------------------

* Add collective.workspace to your buildout eggs.
* Install collective.workspace in the 'Add-ons' section of Plone's Site Setup.
* Enable the behaviour on your dexterity content type (Either using GenericSetup or Site Setup -> Dexterity Content Types).

Compatibility
-------------

For Plone 5.1 and 5.2 you should use version 3.x.
For Plone 4.3 and 5.0 you should use version 2.x.

Custom Workspace Groups
-----------------------

The default groups available on a workspace are 'Guests', 'Members', and 'Admins'.
You can customise the groups that are available editing the registry record ``collective.workspace.available_groups``.
