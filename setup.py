from setuptools import setup, find_packages
import os

version = "4.6.0"

setup(
    name="recensio.theme",
    version=version,
    description="An Diazo theme for Plone 4",
    long_description=open("README.txt").read() + "\n" + open("CHANGES.txt").read(),
    classifiers=["Framework :: Plone", "Programming Language :: Python :: 2.7",],
    keywords="web zope plone theme",
    author="Syslab.com GmbH",
    author_email="info@syslab.com",
    url="http://svn.plone.org/svn/collective/",
    license="GPL",
    packages=find_packages(exclude=["ez_setup"]),
    namespace_packages=["recensio"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "plone.app.theming",
        "plone.api",
        "plone.resource",
        "PyICU",
        "logilab-common",
        "recensio.contenttypes",
        "reportlab",
        "setuptools",
        "Products.CMFPlone",
        "z3c.jbot",
    ],
    extras_require={"test": ["plone.app.testing", "recensio.policy"],},
    entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
)
