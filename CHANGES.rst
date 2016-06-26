Changelog
=========

2.0 (unreleased)
----------------

Changed functionality:

- The `workspace_groups` PAS plugin now stores groups in the same way as normal Plone groups,
  rather than doing catalog queries to find workspaces.
  This performs much better even without enabling caching for the plugin.
  These workspace-based groups are updated automatically as workspace rosters are edited.
  (A separate plugin is used so that listing of workspace groups in the Plone control panel
  can easily be disabled.)
- The Members group is no longer displayed as an option in the UI,
  since it is assigned automatically.
- Copying and pasting a workspace now empties the roster of the copy.

Bugs fixed:

- A change to the `user` of a workspace membership is now handled properly
  (which might need to happen, for example, when merging users).
- Membership fields can now have a `defaultFactory` that is context-aware
  (the field is now bound to the membershp before fetching the default).
- When a user is deleted from the site,
  their memberships in any workspaces are now also deleted.
- New workspace counters can now be added without breaking existing workspaces.

Cleanup:

- Removed code related to caching (`purge_workspace_pas_cache`) that is no longer used.


1.3 (unreleased)
----------------

- Added msgids with i18n domain
- Added German translation
- Show status message after adding, removing or updating a roster entry.


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
