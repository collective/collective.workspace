from setuptools import setup, find_packages

version = "3.0.0"

long_description = (
    open("README.rst").read() + "\n" + "Contributors\n"
    "============\n"
    + "\n"
    + open("CONTRIBUTORS.rst").read()
    + "\n"
    + open("CHANGES.rst").read()
    + "\n"
)

setup(
    name="collective.workspace",
    version=version,
    description="Provide 'membership' in specific areas of a Plone Site",
    long_description=long_description,
    # Get more strings from
    # https://pypi.org/classifiers/
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 5.1",
        "Framework :: Plone :: 5.2",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="plone workspace collaboration",
    author="David Glick",
    author_email="",
    url="https://github.com/collective/collective.workspace",
    license="gpl",
    packages=find_packages("src"),
    package_dir={"": "src"},
    namespace_packages=["collective",],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
        "plone.api",
        "plone.app.dexterity",
        "six",
        # -*- Extra requirements: -*-
    ],
    extras_require={
        "test": ["plone.app.robotframework[debug,reload]", "plone.app.testing",],
        "develop": ["zest.releaser",],
    },
    entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
)
