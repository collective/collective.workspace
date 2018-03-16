from setuptools import setup, find_packages

version = '2.0b1'

long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.rst').read()
    + '\n' +
    open('CHANGES.rst').read()
    + '\n')

setup(name='collective.workspace',
      version=version,
      description="Provide 'membership' in specific areas of a Plone Site",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='plone workspace collaboration',
      author='David Glick',
      author_email='',
      url='https://github.com/collective/collective.workspace',
      license='gpl',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['collective', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.api',
          'plone.app.dexterity',
          'plone.formwidget.autocomplete',
          # -*- Extra requirements: -*-
      ],
      extras_require={
          'test': [
              'plone.app.robotframework',
              'plone.app.testing',
          ],
          'develop': [
              'zest.releaser',
          ],
      },
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
)
