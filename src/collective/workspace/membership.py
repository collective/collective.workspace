from plone.autoform import directives as form
from plone.formwidget.autocomplete import AutocompleteFieldWidget
from plone.supermodel import model
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope import schema


class ITeamMembership(model.Schema):
    """Schema for one person's membership in a team."""

    form.widget(user=AutocompleteFieldWidget)
    user = schema.Choice(
        title=u'User',
        vocabulary='plone.principalsource.Users',
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
