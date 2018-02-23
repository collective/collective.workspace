.. image:: https://travis-ci.org/collective/collective.workspace.svg?branch=master
    :target: https://travis-ci.org/collective/collective.workspace

collective.workspace
====================

Introduction
------------

collective.workspace package for providing 'membership' in specific areas of a Plone Site. 

It allows you to grant people access to areas of content using a membership group rather than local roles for each user, and to delegate control over that group to people who don't have access to the site-wide user/group control panel.

collective.workspace provides a behavior that can be enabled for any Dexterity content type. When enabled, it adds a "Roster" tab which is where you can manage the team. 

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

Custom Workspace Groups
-----------------------

The default groups available on a workspace are 'Guests', 'Members', and 'Admins'. You can customise the groups that are available and the default permissions they are given by adding a custom IWorkspace adapter:

``configure.zcml``

.. code:: xml

  <adapter
     for="mypackage.MyContentType"
     provides="collective.workspace.interfaces.IWorkspace"
     factory=".adapters.MyWorkspace"
     />

``adapters.py``

.. code:: python

  from collective.workspace.workspace import Workspace

  class MyWorkspace(Workspace):
      """
      A custom workspace behaviour, based on collective.workspace
      """
      # A list of groups to which team members can be assigned.
      # Maps group name -> roles
      available_groups = {
          u'Supervillains': ('Reader', ),
          u'Superheroes': ('Reader', 'Contributor', 'Reviewer', 'Editor',),
      }
