#!/bin/sh
#
# Shell script to manage .po files.
#
# Run this file in the folder main __init__.py of product
#
# E.g. if your product is yourproduct.name
# you run this file in yourproduct.name/yourproduct/name
#
#
# Copyright 2010 mFabrik http://mfabrik.com
#
# http://plone.org/documentation/manual/plone-community-developer-documentation/i18n/localization
#

# Assume the product name is the current folder name
CURRENT_PATH=`pwd`
CATALOGNAMES="collective.workspace plone"

# List of languages
LANGUAGES="de"

# Create locales folder structure for languages
install -d locales
for lang in $LANGUAGES; do
    install -d locales/$lang/LC_MESSAGES
done

I18NDUDE=~/Plone/zinstance/bin/i18ndude

if test ! -e $I18NDUDE; then
        echo "You must install i18ndude with buildout"
        echo "See https://github.com/collective/collective.developermanual/blob/master/source/i18n/localization.txt"
        exit
fi

#
# Do we need to merge manual PO entries from a file called manual.pot.
# this option is later passed to i18ndude
#

for catalogname in $CATALOGNAMES; do
    echo "Catalog: ${catalogname}"
    if test -e locales/manual-${catalogname}.pot; then
            echo "Manual PO entries detected"
            MERGE="--merge locales/manual-${catalogname}.pot"
    else
            echo "No manual PO entries detected"
            MERGE=""
    fi
    $I18NDUDE rebuild-pot --pot locales/$catalogname.pot $MERGE --create $catalogname .
    echo ""
done

# Rebuild .pot


# Compile po files
for lang in $(find locales -mindepth 1 -maxdepth 1 -type d); do

    if test -d $lang/LC_MESSAGES; then

        for catalogname in $CATALOGNAMES; do

            PO=$lang/LC_MESSAGES/${catalogname}.po

            # Create po file if not exists
            touch $PO

            # Sync po file
            echo "Syncing $PO"
            $I18NDUDE sync --pot locales/$catalogname.pot $PO
            echo ""

        done
    fi

done
#!/bin/sh
