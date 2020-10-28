.. image:: https://api.travis-ci.com/zopefoundation/Products.MailHost.svg?branch=master
   :target: https://travis-ci.com/zopefoundation/Products.MailHost

.. image:: https://coveralls.io/repos/github/zopefoundation/Products.MailHost/badge.svg?branch=master
   :target: https://coveralls.io/github/zopefoundation/Products.MailHost?branch=master

.. image:: https://img.shields.io/pypi/v/Products.MailHost.svg
   :target: https://pypi.org/project/Products.MailHost/
   :alt: Latest stable release on PyPI

.. image:: https://img.shields.io/pypi/pyversions/Products.MailHost.svg
   :target: https://pypi.org/project/Products.MailHost/
   :alt: Stable release supported Python versions

Products.MailHost
=================

The MailHost product provides support for sending email from within the Zope
environment using MailHost objects.

An optional character set can be specified to automatically encode unicode
input, and perform appropriate RFC 2822 header and body encoding for the
specified character set. Full python email.Message.Message objects may be sent.

Email can optionally be encoded using Base64 or Quoted-Printable encoding
(though automatic body encoding will be applied if a character set is
specified).

Usage
-----

MailHost provides integration with the Zope transaction system and optional
support for asynchronous mail delivery. Asynchronous mail delivery is
implemented using a queue and a dedicated thread processing the queue. The
thread is (re)-started automatically when sending an email. The thread can be
started manually (in case of restart) by calling its
manage_restartQueueThread?action=start method through HTTP. There is currently
no possibility to start the thread at Zope startup time.

Supports TLS/SSL encryption (requires Python compiled with SSL support).

Configuration
-------------

To force MailHost to only queue mails without sending them, activate queuing
in the ZMI and set the environment variable ``MAILHOST_QUEUE_ONLY=1``.
This could be helpful in a staging environment where mails should not be sent.
