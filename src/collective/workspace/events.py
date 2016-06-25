# coding=utf-8
from collective.workspace.pas import purge_workspace_pas_cache
from zope.component.interfaces import ObjectEvent
from zope.globalrequest import getRequest


class TeamMemberEvent(ObjectEvent):
    """Base for team member events.

    This is used instead of normal Zope object lifecycle
    events so it can be dispatched based on the workspace
    rather than based on the modified object (which is
    just a dictionary in this case).
    """

    def __init__(self, object, membership):
        self.object = object
        self.membership = membership


class TeamMemberAddedEvent(TeamMemberEvent):
    """Event for when a member is added."""


class TeamMemberRemovedEvent(TeamMemberEvent):
    """Event for when a member is removed."""


class TeamMemberModifiedEvent(TeamMemberEvent):
    """Event for when a member is modified."""


def on_generic_workspace_event(obj, event):
    ''' When something happens to a workspace,
    we want the pas plugin cache invalidated
    '''
    request = getRequest()
    if not request:
        return
    purge_workspace_pas_cache()
