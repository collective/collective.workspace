from setuptools import find_packages
from setuptools import setup

version = "4.0.0.dev0"

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
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: 6.1",
        "Framework :: Plone :: 6.2",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="plone workspace collaboration",
    author="David Glick",
    author_email="collective@plone.org",
    url="https://github.com/collective/collective.workspace",
    license="gpl",
    packages=find_packages("src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    namespace_packages=["collective"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
        "plone.api",
        "plone.app.dexterity",
        # -*- Extra requirements: -*-
    ],
    extras_require={
        "test": [
            "plone.app.robotframework[debug,reload]",
            "plone.app.testing",
        ],
        "develop": [
            "zest.releaser",
        ],
    },
    entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
)
