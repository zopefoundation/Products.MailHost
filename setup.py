##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from setuptools import find_packages
from setuptools import setup


def _read(fname):
    with open(fname) as fp:
        return fp.read()


setup(
    name='Products.MailHost',
    version='6.1.dev0',
    url='https://github.com/zopefoundation/Products.MailHost',
    project_urls={
        'Issue Tracker': ('https://github.com/zopefoundation'
                          '/Products.MailHost/issues'),
        'Sources': 'https://github.com/zopefoundation/Products.MailHost',
    },
    license='ZPL-2.1',
    description='zope.sendmail integration for Zope.',
    author='Zope Foundation and Contributors',
    author_email='zope-dev@zope.dev',
    long_description=_read('README.rst') + '\n' + _read('CHANGES.rst'),
    packages=find_packages('src'),
    namespace_packages=['Products'],
    package_dir={'': 'src'},
    classifiers=[
        'Development Status :: 6 - Mature',
        'Environment :: Web Environment',
        'Framework :: Zope',
        'Framework :: Zope :: 5',
        'License :: OSI Approved :: Zope Public License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Communications :: Email',
    ],
    python_requires='>=3.9',
    install_requires=[
        'setuptools',
        'AccessControl',
        'Acquisition',
        'DateTime',
        'DocumentTemplate',
        'ExtensionClass>=4.1a1',
        'Persistence',
        'Zope >= 4.0b4',
        'zope.deferredimport',
        'zope.interface',
        'zope.sendmail >= 6.2',
    ],
    extras_require={
        'genericsetup': ['Products.GenericSetup >= 2.0b1'],
    },
    include_package_data=True,
    zip_safe=False,
)
