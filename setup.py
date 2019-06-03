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

from setuptools import setup, find_packages

setup(
    name='Products.MailHost',
    version='2.13.4',
    url='https://github.com/zopefoundation/Products.MailHost',
    license='ZPL 2.1',
    description="zope.sendmail integration for Zope 2.",
    author='Zope Foundation and Contributors',
    author_email='zope-dev@zope.org',
    long_description=open('README.txt').read() + '\n' +
                     open('CHANGES.txt').read(),
    packages=find_packages('src'),
    namespace_packages=['Products'],
    package_dir={'': 'src'},
    install_requires=[
        'setuptools',
        'AccessControl',
        'Acquisition',
        'DateTime',
        'DocumentTemplate',
        'ExtensionClass < 4.0dev',
        'Persistence',
        'Zope2 >= 2.13.0a1',
        'zope.deferredimport',
        'zope.interface',
        'zope.sendmail',
    ],
    include_package_data=True,
    zip_safe=False,
)
