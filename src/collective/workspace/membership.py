from collective.workspace.events import TeamMemberModifiedEvent
from collective.workspace.events import TeamMemberRemovedEvent
from collective.workspace.interfaces import IWorkspace
from collective.workspace.vocabs import UsersSource
from copy import deepcopy
from plone.app.z3cform.interfaces import IAjaxSelectWidget
from plone.app.z3cform.widget import AjaxSelectFieldWidget
from plone.autoform import directives as form
from plone.supermodel import model
from plone.uuid.interfaces import IUUIDGenerator
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.converter import BaseDataConverter
from zope import schema
from zope.component import adapter
from zope.component import getUtility
from zope.event import notify
from zope.interface import implementer
from zope.schema.interfaces import IChoice


class ITeamMembership(model.Schema):
    """Schema for one person's membership in a team."""

    form.widget('user', AjaxSelectFieldWidget)
    user = schema.Choice(
        title=u'User',
        source=UsersSource,
    )

    position = schema.TextLine(
        title=u'Position',
        required=False,
    )

    form.widget(groups=CheckBoxFieldWidget)
    groups = schema.Set(
        title=u'Groups',
        required=False,
        value_type=schema.Choice(
            vocabulary='collective.workspace.groups',
        ),
    )


# We need a pass-through widget converter
# because the default one tries to look up the form value
# as a vocabulary token without binding the field first.
@adapter(IChoice, IAjaxSelectWidget)
class ChoiceAjaxSelectWidgetConverter(BaseDataConverter):

    def toWidgetValue(self, value):
        if not value:
            return self.field.missing_value
        return value

    def toFieldValue(self, value):
        if not value:
            return self.field.missing_value
        return value


@implementer(ITeamMembership)
class TeamMembership(object):

    __slots__ = ('workspace', '__dict__')
    _schema = ITeamMembership

    def __init__(self, workspace, data):
        self.workspace = workspace
        if 'UID' not in data:
            data['UID'] = getUtility(IUUIDGenerator)()
        self.__dict__ = data

    def __getattr__(self, name):
        field = self.__class__._schema.get(name, None)
        if field is None:
            raise AttributeError(name)
        return deepcopy(field.default)

    def update(self, data):
        old = self.__dict__.copy()
        self.__dict__.update(data)
        # make sure change is persisted
        # XXX really we should use PersistentDicts
        workspace = self.workspace
        workspace.context._team[self.user] = self.__dict__

        # update counters
        for name, func in workspace.counters:
            # The following is based on Python's ability to treat booleans
            # as integers (1 or 0)...
            # 0 = no change
            # 1 = matches now but didn't before
            # -1 = matched before but doesn't now
            # Then we use that difference to update the count of how many roster members match.
            diff = func(self.__dict__) - func(old)
            if diff:
                workspace.context._counters[name].change(diff)

        self.handle_modified(old)
        notify(TeamMemberModifiedEvent(self.workspace.context, self))

    def handle_added(self):
        pass

    def handle_modified(self, old):
        pass

    def handle_removed(self):
        pass

    def remove_from_team(self):
        workspace = self.workspace
        for name, func in workspace.counters:
            if func(self.__dict__):
                workspace.context._counters[name].change(-1)
        del self.workspace.members[self.user]
        self.handle_removed()
        notify(TeamMemberRemovedEvent(self.workspace.context, self))
        self.workspace.context.reindexObject(idxs=['workspace_members'])


@adapter(ITeamMembership)
@implementer(IWorkspace)
def workspace_from_membership(membership):
    return membership.workspace
