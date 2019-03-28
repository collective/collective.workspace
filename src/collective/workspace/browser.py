from AccessControl import getSecurityManager
from Products.statusmessages.interfaces import IStatusMessage
from collective.workspace.interfaces import _
from collective.workspace.interfaces import IRosterView
from collective.workspace.interfaces import IWorkspace
from collections import namedtuple
from plone.autoform.base import AutoFields
from plone.autoform.form import AutoExtensibleForm
from plone.z3cform import z2
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from z3c.form.form import DisplayForm
from z3c.form.form import EditForm
from z3c.form.interfaces import ActionExecutionError
from zope.cachedescriptors.property import Lazy as lazy_property
from zope.interface import implementer
from zope.publisher.interfaces.browser import IPublishTraverse
import transaction


Action = namedtuple('Action', "label view_name permission")


@implementer(IRosterView)
class TeamRosterView(AutoFields, DisplayForm):
    """Display the roster as a table."""

    row_template = ViewPageTemplateFile('templates/team_roster_row.pt')

    row_actions = (
        Action('Edit', 'edit-roster', 'collective.workspace: Manage roster'),
    )

    table_actions = ()

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.workspace = IWorkspace(self.context)

    @property
    def label(self):
        return _(u'Roster: ${title}', mapping={'title': self.context.Title()})

    @lazy_property
    def schema(self):
        return self.workspace.membership_schema

    ignoreContext = True

    def getContent(self):
        return self.context

    def row_views(self):
        for membership in self.workspace:
            for widget in self.widgets.values():
                widget.ignoreContext = False
                widget.context = membership
                widget.update()
            yield self.row_template(membership=membership)

    @lazy_property
    def can_edit_roster(self):
        return getSecurityManager().checkPermission(
            'collective.workspace: Manage roster', self.context)

    def update(self):
        z2.switch_on(self)
        self.updateFieldsFromSchemata()
        self.updateWidgets()

    def render(self):
        return self.index()

    def __call__(self):
        self.update()
        return self.render()


@implementer(IPublishTraverse)
class TeamMemberEditForm(AutoExtensibleForm, EditForm):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.workspace = IWorkspace(self.context)

    key = None

    def publishTraverse(self, request, name):
        self.key = name
        return self

    @lazy_property
    def schema(self):
        return self.workspace.membership_schema

    def updateFields(self):
        super(TeamMemberEditForm, self).updateFields()
        # don't show the user field if we are editing
        if self.key:
            del self.fields['user']

    @lazy_property
    def ignoreContext(self):
        return not bool(self.key)

    @lazy_property
    def label(self):
        if self.key:
            return self.getContent()._title
        else:
            return _(u'Add Person to Roster')

    @lazy_property
    def _content(self):
        if not self.key:
            return self.context
        workspace = self.workspace
        memberdata = workspace.members[self.key]
        return workspace.membership_factory(workspace, memberdata)

    def getContent(self):
        return self._content

    def validateInvariants(self, membership):
        pass

    @button.buttonAndHandler(_(u'Save'))
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        status = _(u'Changes saved')

        if self.key:
            membership = self.getContent()
            membership.update(data)
        else:
            # Add new roster member
            membership = self.workspace.add_to_team(**data)
            status = _(u'User added')

        try:
            self.validateInvariants(membership)
        except ActionExecutionError:
            # make sure above changes won't be persisted
            transaction.abort()
            raise

        self._finished = True
        IStatusMessage(self.request).addStatusMessage(status, 'info')

    @property
    def can_remove(self):
        return self.key

    @button.buttonAndHandler(
        _(u'Remove'), condition=lambda self: self.can_remove)
    def handleRemove(self, action):
        membership = self.getContent()
        membership.remove_from_team()
        self._finished = True
        IStatusMessage(self.request).addStatusMessage(
            _(u"User removed"), "info")

    _finished = False

    def render(self):
        if self._finished:
            return ' '
        return super(TeamMemberEditForm, self).render()
