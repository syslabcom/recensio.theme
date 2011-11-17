from setuptools import setup, find_packages
import os

version = '2.1.2dev'

setup(name='recensio.theme',
      version=version,
      description="An installable theme for Plone 3",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='web zope plone theme',
      author='Syslab.com GmbH',
      author_email='info@syslab.com',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['recensio'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'collective.xdv',
          'logilab-common',
          'recensio.contenttypes',
          'reportlab',
          'setuptools',
      ],
      extras_require={
        "test" : "plone.app.testing"
        },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins = ["ZopeSkel"],
      )
