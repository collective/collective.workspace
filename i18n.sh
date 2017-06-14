#!/usr/bin/env bash
bin/i18ndude rebuild-pot --pot src/collective/workspace/locales/collective.workspace.pot --merge src/collective/workspace/locales/manual-collective.workspace.pot --create collective.workspace src/collective/workspace
bin/i18ndude sync --pot src/collective/workspace/locales/collective.workspace.pot src/collective/workspace/locales/*/LC_MESSAGES/collective.workspace.po

bin/i18ndude rebuild-pot --pot src/collective/workspace/locales/plone.pot --merge src/collective/workspace/locales/manual-plone.pot --create plone src/collective/workspace
bin/i18ndude sync --pot src/collective/workspace/locales/plone.pot src/collective/workspace/locales/*/LC_MESSAGES/plone.po

bin/pocompile
