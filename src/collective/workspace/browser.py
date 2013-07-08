from AccessControl import getSecurityManager
from Acquisition import ImplicitAcquisitionWrapper
from collective.workspace.interfaces import IWorkspace
from collective.workspace.events import TeamMemberAddedEvent
from collective.workspace.events import TeamMemberModifiedEvent
from collective.workspace.events import TeamMemberRemovedEvent
from plone.app.uuid.utils import uuidToURL
from plone.autoform.form import AutoExtensibleForm
from plone.z3cform.crud import crud
from plone.z3cform.layout import wrap_form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from z3c.form import field
from z3c.form import form
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope.cachedescriptors.property import Lazy as lazy_property
from zope.event import notify
import copy


class TeamRosterEditSubForm(crud.EditSubForm):
    template = ViewPageTemplateFile('templates/team_roster_row.pt')

    @property
    def fields(self):
        crud_form = self.context.context
        if crud_form.can_edit_roster:
            fields = field.Fields(self._select_field())
            fields += field.Fields(crud_form.membership_schema)
            fields['user'].mode = 'display'
            fields['groups'].widgetFactory = CheckBoxFieldWidget
        else:
            fields = field.Fields(crud_form.membership_schema)
            for f in fields.values():
                f.mode = 'display'

        return fields

    def applyChanges(self, data):
        changes = super(TeamRosterEditSubForm, self).applyChanges()
        if changes:
            workspace_context = self.context.context.context
            notify(TeamMemberModifiedEvent(workspace_context, data))


class TeamRosterEditForm(crud.EditForm):
    template = ViewPageTemplateFile('templates/team_roster_table.pt')
    editsubform_factory = TeamRosterEditSubForm

    @property
    def label(self):
        return 'Roster: ' + self.context.context.Title()

    # Make sure we mutate our own copies of the buttons
    form.extends(crud.EditForm)

    buttons = copy.deepcopy(crud.EditForm.buttons)
    buttons['edit'].condition = lambda form: form.context.can_edit_roster
    buttons['delete'].condition = lambda form: form.context.can_edit_roster


class TeamRosterForm(AutoExtensibleForm, crud.CrudForm):
    """Form for managing the team roster."""
    editform_factory = TeamRosterEditForm
    addform_factory = crud.NullForm

    template = ViewPageTemplateFile('templates/team_roster.pt')

    @lazy_property
    def workspace(self):
        return IWorkspace(self.context)

    @lazy_property
    def membership_schema(self):
        return self.workspace.membership_schema
    schema = membership_schema

    ignoreContext = True

    @lazy_property
    def can_edit_roster(self):
        return getSecurityManager().checkPermission('collective.workspace: Manage roster', self.context)

    def update(self):
        AutoExtensibleForm.update(self)
        crud.CrudForm.update(self)

    @lazy_property
    def update_schema(self):
        fields = field.Fields(self.membership_schema)
        if self.can_edit_roster:
            fields = fields.omit('user')
        return fields

    @lazy_property
    def view_schema(self):
        fields = field.Fields(self.membership_schema)
        if self.can_edit_roster:
            fields = fields.select('user')
        return fields

    def get_items(self):
        return [(user_id, ImplicitAcquisitionWrapper(membership, self.context))
                for user_id, membership
                in self.workspace.members.items()]

    @button.buttonAndHandler(u'Add team member')
    def handleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            return

        user_id = str(data['user'])
        self.workspace.members[user_id] = data
        notify(TeamMemberAddedEvent(self.context, data))
        self.context.reindexObject(idxs=['workspace_members'])

    def remove(self, (id, item)):
        del self.workspace.members[id]
        notify(TeamMemberRemovedEvent(self.context, item))
        self.context.reindexObject(idxs=['workspace_members'])

    def link(self, item, fname):
        if fname == 'user':
            return uuidToURL(item['user'])

TeamRosterPage = wrap_form(TeamRosterForm)
