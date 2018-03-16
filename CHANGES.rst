Changelog
=========

2.0b1 (2018-03-16)
------------------

Changed functionality:

- The `workspace_groups` PAS plugin now stores groups in the same way as normal Plone groups,
  rather than doing catalog queries to find workspaces.
  This performs much better even without enabling caching for the plugin.
  These workspace-based groups are updated automatically as workspace rosters are edited.
  (A separate plugin is used so that listing of workspace groups in the Plone control panel
  can easily be disabled.)
- The Members group is no longer displayed as an option in the UI,
  since it is assigned automatically. Other automatic workspace groups can be
  configured with arbitrary conditions for inclusion in the group.
- Copying and pasting a workspace now empties the roster of the copy.
- Trying to set a membership attribute directly now raises an exception.
  Membership attributes should be updated using the `update` method
  to make sure that all changes are properly accounted for.
- A last modified time is now tracked for each roster membership.
- It's now possible to add a roster entry that isn't associated with a user
  (for example, to represent a person who doesn't have a Plone account).

Bugs fixed:

- A change to the `user` of a workspace membership is now handled properly
  (which might need to happen, for example, when merging users).
- Membership fields can now have a `defaultFactory` that is context-aware
  (the field is now bound to the membershp before fetching the default).
- When a user is deleted from the site,
  their memberships in any workspaces are now also deleted.
- New workspace counters can now be added without breaking existing workspaces.
- Tools are now looked up using `plone.api.portal.get_tool`,
  which helps in some cases where objects are not properly acquisition-wrapped.
- Make sure UID doesn't get reset when calling add_to_team
  with a user who is already in the workspace.

Cleanup:

- Removed code related to caching (`purge_workspace_pas_cache`) that is no longer used.


1.4 (unreleased)
----------------

- Nothing changed yet.


1.3 (2016-06-29)
----------------

- Added msgids with i18n domain
- Added German translation
- Show status message after adding, removing or updating a roster entry.
- Fixed issues with caching


1.2 (2016-06-22)
----------------

- Performance improvements
- Intelligent caching of groups, plus cache invalidation on changes to a workspace
- Added a new role TeamGuest that can be used to grant reduced access
  permissions to a workspace


1.1 (2014-07-04)
----------------

- Fixed distribution issues


1.0 (2014-07-04)
----------------

- Initial release
