##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""SendMailTag unit tests.
"""


import unittest

from OFS.DTMLMethod import addDTMLMethod
from Testing.ZopeTestCase import ZopeLite

from .dummy import DummyMailHost


class SendMailTagTests(unittest.TestCase):

    def setUp(self):
        self.app = ZopeLite.app()
        self.app._setObject('MailHost', DummyMailHost('MailHost'))

    def _getTargetClass(self):
        from Products.MailHost.SendMailTag import SendMailTag
        return SendMailTag

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_instantiation(self):
        blocks = [('sendmail', 'mailhost="MailHost"', None)]
        tag = self._makeOne(blocks, encoding='latin-1')

        self.assertEqual(tag.encoding, 'latin-1')
        self.assertEqual(tag.mailhost, 'MailHost')
        self.assertEqual(tag.mailto, '')
        self.assertEqual(tag.mailfrom, '')
        self.assertEqual(tag.subject, '')
        self.assertEqual(tag.port, 25)

    def test_instantiation_full(self):
        blocks = [('sendmail',
                   ('smtphost="localhost" '
                    'port=1025 '
                    'mailto="recipient@test.com" '
                    'mailfrom="sender@test.com" '
                    'subject="Test Email" '
                    'encode="base64" '),
                   None)]
        tag = self._makeOne(blocks)
        self.assertEqual(tag.encoding, None)
        self.assertEqual(tag.smtphost, 'localhost')
        self.assertEqual(tag.mailto, 'recipient@test.com')
        self.assertEqual(tag.mailfrom, 'sender@test.com')
        self.assertEqual(tag.subject, 'Test Email')
        self.assertEqual(tag.port, 1025)

    def test_dtml_var(self):
        addDTMLMethod(self.app, 'testing',
                      file=('<dtml-sendmail mailhost="MailHost">'
                            'To: person@their.machine.com\n'
                            'From: me@mymachine.net\n'
                            'Subject: just called to say...\n'
                            'Date: Thu, 16 May 2019 16:04:14 -0500\n'
                            '\n'
                            'boy howdy!\n'
                            '</dtml-sendmail>'))
        self.app.testing(client=self.app)
        outmsg = self.app.MailHost.sent
        inmsg = (b'To: person@their.machine.com\n'
                 b'From: me@mymachine.net\n'
                 b'Subject: just called to say...\n'
                 b'Date: Thu, 16 May 2019 16:04:14 -0500\n'
                 b'\n'
                 b'boy howdy!\n')

        inmsg = inmsg.replace(b"\n", b"\r\n")

        self.assertEqual(outmsg, inmsg)
