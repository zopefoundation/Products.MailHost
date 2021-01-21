Changelog
=========

4.11 (2021-01-21)
-----------------

- Use standard conforming ``\r\n`` line endings.
  This may require adaptations in testsSupport messages with line separation ``\r\n``
  (`#35 <https://github.com/zopefoundation/Products.MailHost/issues/35>`_).



4.10 (2020-07-31)
-----------------

- We depend on ``zope.sendmail >= 5.1``.

- Support messages with explicit ``Content-Transfer-Encoding: 8bit``
  (`#30 <https://github.com/zopefoundation/Products.MailHost/issues/30>`_).
  


4.9 (2020-02-12)
----------------

- Fix DeprecationWarnings from ``DocumentTemplate`` with import changes


4.8 (2020-01-06)
----------------

- Show a hint in the ZMI if the delivery queue is forced to queue-only mode
  (`#25 <https://github.com/zopefoundation/Products.MailHost/issues/25>`_)

- Improve the asynchronous delivery information on the ZMI Edit tab
  (`#24 <https://github.com/zopefoundation/Products.MailHost/issues/24>`_)

- Fix queued mail delivery with just a single string receiver email
  (`#26 <https://github.com/zopefoundation/Products.MailHost/issues/26>`_)

- Fix Flake8 issues.
  (`#22 <https://github.com/zopefoundation/Products.MailHost/issues/22>`_)


4.7 (2019-06-03)
----------------

- Do not start QueueProcessorThread on configuration update.
  (`#14 <https://github.com/zopefoundation/Products.MailHost/issues/14>`_)


4.6 (2019-05-16)
----------------

- Fix breaking sendmail tag rendering with DocumentTemplate > 3


4.5 (2019-04-07)
----------------

- Prevent ZMI blowups when pointing to a non-Maildir queue folder
  (`#2 <https://github.com/zopefoundation/Products.MailHost/issues/2>`_)

- Changed ZMI forms for Zope 4 ZMI compliance
  (`#17 <https://github.com/zopefoundation/Products.MailHost/issues/17>`_)

- Packaging and test configuration cleanup

- Add badges to the README


4.4 (2019-04-03)
----------------

- Add ability to disable sending of queued mails. Details see README.rst.
  (`#14 <https://github.com/zopefoundation/Products.MailHost/issues/14>`_)


4.3 (2019-03-08)
----------------

- silence deprecation warning due to non-raw regex
  (`#13 <https://github.com/zopefoundation/Products.MailHost/issues/13>`_)

- Specify supported Python versions using ``python_requires`` in setup.py
  (`Zope#481 <https://github.com/zopefoundation/Zope/issues/481>`_)

- Add support for Python 3.8


4.2 (2018-10-05)
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
