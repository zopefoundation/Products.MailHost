Changelog
=========

4.2 (unreleased)
----------------

- Add icon for Bootstrap ZMI.

- Fix start-up in case ``Products.GenericSetup`` is not installed.
  (`#9 <https://github.com/zopefoundation/Products.MailHost/issues/9>`_)

- Add support for Python 3.7.


4.1 (2018-05-20)
----------------

- Fix GenericSetup support for GenericSetup 2.x

- Fix DeprecationWarnings

- PEP-8 code style compliance

- Drop support for Python 3.4


4.0 (2017-09-14)
----------------

- Move GenericSetup export/import support from the GenericSetup package
  to MailHost as a setuptools extra.

- Python 3 compatibility

- Require Zope 4, aka drop Zope 2.13 support.

- add test coverage reporting

- Use `@implementer` class decorator.

- Drop long-deprecated support for uuencoded emails.

3.0 (2016-07-18)
----------------

- Remove HelpSys support.

2.13.2 (2014-11-02)
-------------------

- Adjust tests to pass with latest zope.sendmail versions.

- Specify detailed distribution dependencies.

2.13.1 (2010-09-25)
-------------------

- LP #642728: Fixed TypeError on nested multi part messages in MailHost.

2.13.0 (2010-07-13)
-------------------

- Released as separate package.
