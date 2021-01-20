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
"""MailHost unit tests.
"""

import os.path
import shutil
import sys
import tempfile
import unittest
from email import message_from_string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import six

import transaction
import zope.sendmail.maildir

from ..MailHost import MailHost
from ..MailHost import MailHostError
from ..MailHost import _mungeHeaders
from .dummy import DummyMailHost
from .dummy import FakeContent


# Appease flake8
if six.PY2:
    unicode = unicode  # noqa: F821
    parse_message = message_from_string
else:
    unicode = str
    from email import message_from_bytes
    parse_message = message_from_bytes

PY36 = sys.version_info[0:2] >= (3, 6)


class TestMailHost(unittest.TestCase):

    def _getTargetClass(self):
        return DummyMailHost

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_z3interfaces(self):
        from zope.interface.verify import verifyClass

        from Products.MailHost.interfaces import IMailHost

        verifyClass(IMailHost, self._getTargetClass())

    def testAllHeaders(self):
        msg = """To: recipient@example.com
From: sender@example.com
Subject: This is the subject

This is the message body."""
        # No additional info
        resmsg, resto, resfrom = _mungeHeaders(msg)
        self.assertEqual(resto, ['recipient@example.com'])
        self.assertEqual(resfrom, 'sender@example.com')

        # Add duplicated info
        resmsg, resto, resfrom = _mungeHeaders(
            msg, 'recipient@example.com',
            'sender@example.com', 'This is the subject')
        self.assertEqual(resto, ['recipient@example.com'])
        self.assertEqual(resfrom, 'sender@example.com')

        # Add extra info
        resmsg, resto, resfrom = _mungeHeaders(
            msg, 'recipient2@example.com',
            'sender2@example.com', 'This is the real subject')
        self.assertEqual(resto, ['recipient2@example.com'])
        self.assertEqual(resfrom, 'sender2@example.com')

    def testMissingHeaders(self):
        msg = """X-Header: Dummy header

This is the message body."""
        # Doesn't specify to
        with self.assertRaises(MailHostError):
            _mungeHeaders(msg, mfrom='sender@example.com')
        # Doesn't specify from
        with self.assertRaises(MailHostError):
            _mungeHeaders(msg, mto='recipient@example.com')

    def testNoHeaders(self):
        msg = """This is the message body."""
        # Doesn't specify to
        with self.assertRaises(MailHostError):
            _mungeHeaders(msg, mfrom='sender@example.com')
        # Doesn't specify from
        with self.assertRaises(MailHostError):
            _mungeHeaders(msg, mto='recipient@example.com')
        # Specify all
        resmsg, resto, resfrom = _mungeHeaders(
            msg, 'recipient2@example.com',
            'sender2@example.com', 'This is the real subject')
        self.assertEqual(resto, ['recipient2@example.com'])
        self.assertEqual(resfrom, 'sender2@example.com')

    def testBCCHeader(self):
        msg = 'From: me@example.com\nBcc: many@example.com\n\nMessage text'
        # Specify only the "Bcc" header.  Useful for bulk emails.
        resmsg, resto, resfrom = _mungeHeaders(msg)
        self.assertEqual(resto, ['many@example.com'])
        self.assertEqual(resfrom, 'me@example.com')

    def test__getThreadKey_uses_fspath(self):
        mh1 = self._makeOne('mh1')
        mh1.smtp_queue_directory = '/abc'
        mh1.absolute_url = lambda self: 'http://example.com/mh1'
        mh2 = self._makeOne('mh2')
        mh2.smtp_queue_directory = '/abc'
        mh2.absolute_url = lambda self: 'http://example.com/mh2'
        self.assertEqual(mh1._getThreadKey(), mh2._getThreadKey())

    def testAddressParser(self):
        msg = """\
To: "Name, Nick" <recipient@example.com>, "Foo Bar" <foo@example.com>
CC: "Web, Jack" <jack@web.com>
From: sender@example.com
Subject: This is the subject

This is the message body."""

        # Test Address-Parser for To & CC given in messageText

        resmsg, resto, resfrom = _mungeHeaders(msg)
        self.assertEqual(
            resto, ['"Name, Nick" <recipient@example.com>',
                    'Foo Bar <foo@example.com>',
                    '"Web, Jack" <jack@web.com>'])
        self.assertEqual(resfrom, 'sender@example.com')

        # Test Address-Parser for a given mto-string

        resmsg, resto, resfrom = _mungeHeaders(
            msg,
            mto='"Public, Joe" <pjoe@example.com>, Foo Bar <foo@example.com>')

        self.assertEqual(
            resto, ['"Public, Joe" <pjoe@example.com>',
                    'Foo Bar <foo@example.com>'])
        self.assertEqual(resfrom, 'sender@example.com')

    def testSendMessageOnly(self):
        msg = """\
To: "Name, Nick" <recipient@example.com>, "Foo Bar" <foo@example.com>
From: sender@example.com
Subject: This is the subject
Date: Sun, 27 Aug 2006 17:00:00 +0200

This is the message body."""

        mailhost = self._makeOne('MailHost')
        mailhost.send(msg)
        if six.PY3:
            msg = msg.encode().replace(b"\n", b"\r\n")
        self.assertEqual(mailhost.sent, msg)

    def testSendWithArguments(self):
        inmsg = """\
Date: Sun, 27 Aug 2006 17:00:00 +0200

This is the message body."""

        outmsg = b"""\
Date: Sun, 27 Aug 2006 17:00:00 +0200
Subject: This is the subject
To: "Name, Nick" <recipient@example.com>, Foo Bar <foo@example.com>
From: sender@example.com

This is the message body."""

        mailhost = self._makeOne('MailHost')
        mailhost.send(messageText=inmsg,
                      mto='"Name, Nick" <recipient@example.com>, '
                          '"Foo Bar" <foo@example.com>',
                      mfrom='sender@example.com',
                      subject='This is the subject')

        if six.PY3:
            outmsg = outmsg.replace(b"\n", b"\r\n")

        self.assertEqual(mailhost.sent, outmsg)

    def testSendWithMtoList(self):
        inmsg = """\
Date: Sun, 27 Aug 2006 17:00:00 +0200

This is the message body."""

        outmsg = b"""\
Date: Sun, 27 Aug 2006 17:00:00 +0200
Subject: This is the subject
To: "Name, Nick" <recipient@example.com>, Foo Bar <foo@example.com>
From: sender@example.com

This is the message body."""

        mailhost = self._makeOne('MailHost')
        mailhost.send(messageText=inmsg,
                      mto=['"Name, Nick" <recipient@example.com>',
                           '"Foo Bar" <foo@example.com>'],
                      mfrom='sender@example.com',
                      subject='This is the subject')

        if six.PY3:
            outmsg = outmsg.replace(b"\n", b"\r\n")

        self.assertEqual(mailhost.sent, outmsg)

    def testSimpleSend(self):
        outmsg = """\
From: sender@example.com
To: "Name, Nick" <recipient@example.com>, "Foo Bar" <foo@example.com>
Subject: This is the subject

This is the message body."""

        mailhost = self._makeOne('MailHost')
        mailhost.simple_send(mto='"Name, Nick" <recipient@example.com>, '
                                 '"Foo Bar" <foo@example.com>',
                             mfrom='sender@example.com',
                             subject='This is the subject',
                             body='This is the message body.')
        self.assertEqual(mailhost.sent, outmsg)
        self.assertEqual(mailhost.immediate, False)

    def testSendImmediate(self):
        outmsg = """\
From: sender@example.com
To: "Name, Nick" <recipient@example.com>, "Foo Bar" <foo@example.com>
Subject: This is the subject

This is the message body."""

        mailhost = self._makeOne('MailHost')
        mailhost.simple_send(mto='"Name, Nick" <recipient@example.com>, '
                                 '"Foo Bar" <foo@example.com>',
                             mfrom='sender@example.com',
                             subject='This is the subject',
                             body='This is the message body.',
                             immediate=True)
        self.assertEqual(mailhost.sent, outmsg)
        self.assertEqual(mailhost.immediate, True)

    def testSendBodyWithUrl(self):
        # The implementation of rfc822.Message reacts poorly to
        # message bodies containing ':' characters as in a url
        msg = "Here's a nice link: http://www.zope.org/"

        mailhost = self._makeOne('MailHost')
        mailhost.send(messageText=msg,
                      mto='"Name, Nick" <recipient@example.com>, '
                          '"Foo Bar" <foo@example.com>',
                      mfrom='sender@example.com',
                      subject='This is the subject')
        out = parse_message(mailhost.sent)
        self.assertEqual(out.get_payload(), msg)
        self.assertEqual(
            out['To'],
            '"Name, Nick" <recipient@example.com>, Foo Bar <foo@example.com>')
        self.assertEqual(out['From'], 'sender@example.com')

    def testSendEncodedBody(self):
        # If a charset is specified the correct headers for content
        # encoding will be set if not already set.  Additionally, if
        # there is a default transfer encoding for the charset, then
        # the content will be encoded and the transfer encoding header
        # will be set.
        msg = b"Here's some encoded t\xc3\xa9xt."
        mailhost = self._makeOne('MailHost')
        mailhost.send(messageText=msg,
                      mto='"Name, Nick" <recipient@example.com>, '
                          '"Foo Bar" <foo@example.com>',
                      mfrom='sender@example.com',
                      subject='This is the subject',
                      charset='utf-8')
        out = parse_message(mailhost.sent)
        self.assertEqual(
            out['To'],
            '"Name, Nick" <recipient@example.com>, Foo Bar <foo@example.com>')
        self.assertEqual(out['From'], 'sender@example.com')
        # utf-8 will default to Quoted Printable encoding
        self.assertEqual(out['Content-Transfer-Encoding'],
                         'quoted-printable')
        self.assertEqual(out['Content-Type'],
                         'text/plain; charset="utf-8"')
        self.assertEqual(out.get_payload(),
                         "Here's some encoded t=C3=A9xt.")

    def testEncodedHeaders(self):
        # Headers are encoded automatically, email headers are encoded
        # piece-wise to ensure the addresses remain ASCII
        mfrom = b'Jos\xc3\xa9 Andr\xc3\xa9s <jose@example.com>'
        mto = b'Ferran Adri\xc3\xa0 <ferran@example.com>'
        subject = b'\xc2\xbfEsferificaci\xc3\xb3n?'
        mailhost = self._makeOne('MailHost')
        mailhost.send(messageText='A message.', mto=mto, mfrom=mfrom,
                      subject=subject, charset='utf-8')
        out = parse_message(mailhost.sent)
        self.assertEqual(
            out['To'],
            '=?utf-8?q?Ferran_Adri=C3=A0?= <ferran@example.com>')
        self.assertEqual(
            out['From'],
            '=?utf-8?q?Jos=C3=A9_Andr=C3=A9s?= <jose@example.com>')
        self.assertEqual(
            out['Subject'],
            '=?utf-8?q?=C2=BFEsferificaci=C3=B3n=3F?=')
        # utf-8 will default to Quoted Printable encoding
        self.assertEqual(out['Content-Transfer-Encoding'],
                         'quoted-printable')
        self.assertEqual(out['Content-Type'],
                         'text/plain; charset="utf-8"')
        self.assertEqual(out.get_payload(), 'A message.')

    def testAlreadyEncodedMessage(self):
        # If the message already specifies encodings, it is
        # essentially not altered this is true even if charset or
        # msg_type is specified
        msg = """\
From: =?utf-8?q?Jos=C3=A9_Andr=C3=A9s?= <jose@example.com>
To: =?utf-8?q?Ferran_Adri=C3=A0?= <ferran@example.com>
Subject: =?utf-8?q?=C2=BFEsferificaci=C3=B3n=3F?=
Date: Sun, 27 Aug 2006 17:00:00 +0200
Content-Type: text/html; charset="utf-8"
Content-Transfer-Encoding: base64
MIME-Version: 1.0 (Generated by testMailHost.py)

wqFVbiB0cnVjbyA8c3Ryb25nPmZhbnTDoXN0aWNvPC9zdHJvbmc+IQ=3D=3D
"""
        mailhost = self._makeOne('MailHost')
        mailhost.send(messageText=msg)
        outmsg = msg
        if six.PY3:
            outmsg = outmsg.encode().replace(b"\n", b"\r\n")
        self.assertEqual(mailhost.sent, outmsg)
        mailhost.send(messageText=msg, msg_type='text/plain')
        # The msg_type is ignored if already set
        self.assertEqual(mailhost.sent, outmsg)

    def testAlreadyEncodedMessageWithCharset(self):
        # If the message already specifies encodings, it is
        # essentially not altered this is true even if charset or
        # msg_type is specified
        msg = """\
From: =?utf-8?q?Jos=C3=A9_Andr=C3=A9s?= <jose@example.com>
To: =?utf-8?q?Ferran_Adri=C3=A0?= <ferran@example.com>
Subject: =?utf-8?q?=C2=BFEsferificaci=C3=B3n=3F?=
Date: Sun, 27 Aug 2006 17:00:00 +0200
Content-Type: text/html; charset="utf-8"
Content-Transfer-Encoding: base64
MIME-Version: 1.0 (Generated by testMailHost.py)

wqFVbiB0cnVjbyA8c3Ryb25nPmZhbnTDoXN0aWNvPC9zdHJvbmc+IQ=3D=3D
"""
        mailhost = self._makeOne('MailHost')
        # Pass a different charset, which will apply to any explicitly
        # set headers
        mailhost.send(messageText=msg,
                      subject='\xbfEsferificaci\xf3n?',
                      charset='iso-8859-1', msg_type='text/plain')
        # The charset for the body should remain the same, but any
        # headers passed into the method will be encoded using the
        # specified charset
        out = parse_message(mailhost.sent)
        self.assertEqual(out['Content-Type'], 'text/html; charset="utf-8"')
        self.assertEqual(out['Content-Transfer-Encoding'], 'base64')
        # Headers set by parameter will be set using charset parameter
        self.assertEqual(out['Subject'],
                         '=?iso-8859-1?q?=BFEsferificaci=F3n=3F?=')
        # original headers will be unaltered
        self.assertEqual(
            out['From'],
            '=?utf-8?q?Jos=C3=A9_Andr=C3=A9s?= <jose@example.com>')

    @unittest.skipIf(six.PY3, 'Test not applicable on Python 3.')
    def testUnicodeMessage(self):
        # unicode messages and headers are decoded using the given charset
        msg = unicode("Here's some unencoded <strong>t\xc3\xa9xt</strong>.",
                      'utf-8')
        mfrom = unicode('Ferran Adri\xc3\xa0 <ferran@example.com>', 'utf-8')
        subject = unicode('\xc2\xa1Andr\xc3\xa9s!', 'utf-8')
        mailhost = self._makeOne('MailHost')
        mailhost.send(messageText=msg,
                      mto='"Name, Nick" <recipient@example.com>',
                      mfrom=mfrom, subject=subject, charset='utf-8',
                      msg_type='text/html')
        out = parse_message(mailhost.sent)
        self.assertEqual(
            out['To'], '"Name, Nick" <recipient@example.com>')
        self.assertEqual(
            out['From'],
            '=?utf-8?q?Ferran_Adri=C3=A0?= <ferran@example.com>')
        self.assertEqual(out['Subject'], '=?utf-8?q?=C2=A1Andr=C3=A9s!?=')
        self.assertEqual(out['Content-Transfer-Encoding'],
                         'quoted-printable')
        self.assertEqual(out['Content-Type'], 'text/html; charset="utf-8"')
        self.assertEqual(
            out.get_payload(),
            "Here's some unencoded <strong>t=C3=A9xt</strong>.")

    @unittest.skipIf(six.PY3, 'Test not applicable on Python 3.')
    def testUnicodeNoEncodingErrors(self):
        # Unicode messages and headers raise errors if no charset is passed to
        # send
        msg = unicode("Here's some unencoded <strong>t\xc3\xa9xt</strong>.",
                      'utf-8')
        subject = unicode('\xc2\xa1Andr\xc3\xa9s!', 'utf-8')
        mailhost = self._makeOne('MailHost')
        self.assertRaises(UnicodeEncodeError,
                          mailhost.send, msg,
                          mto='"Name, Nick" <recipient@example.com>',
                          mfrom='Foo Bar <foo@example.com>',
                          subject=subject)

    def testUnicodeDefaultEncoding(self):
        # However if we pass unicode that can be encoded to the
        # default encoding (generally 'us-ascii'), no error is raised.
        # We include a date in the messageText to make inspecting the
        # results more convenient.
        msg = u"""\
Date: Sun, 27 Aug 2006 17:00:00 +0200

Here's some unencoded <strong>text</strong>."""
        subject = u'Andres!'
        mailhost = self._makeOne('MailHost')
        mailhost.send(msg, mto=u'"Name, Nick" <recipient@example.com>',
                      mfrom=u'Foo Bar <foo@example.com>', subject=subject)
        out = mailhost.sent
        # Ensure the results are not unicode
        inmsg = b"""\
Date: Sun, 27 Aug 2006 17:00:00 +0200
Subject: Andres!
To: "Name, Nick" <recipient@example.com>
From: Foo Bar <foo@example.com>

Here's some unencoded <strong>text</strong>."""

        if six.PY3:
            inmsg = inmsg.replace(b"\n", b"\r\n")

        self.assertEqual(out, inmsg)
        self.assertEqual(type(out), bytes)

    def testSendMessageObject(self):
        # send will accept an email.Message.Message object directly
        msg = message_from_string("""\
From: =?utf-8?q?Jos=C3=A9_Andr=C3=A9s?= <jose@example.com>
To: =?utf-8?q?Ferran_Adri=C3=A0?= <ferran@example.com>
Subject: =?utf-8?q?=C2=BFEsferificaci=C3=B3n=3F?=
Date: Sun, 27 Aug 2006 17:00:00 +0200
Content-Type: text/html; charset="utf-8"
Content-Transfer-Encoding: base64
MIME-Version: 1.1

wqFVbiB0cnVjbyA8c3Ryb25nPmZhbnTDoXN0aWNvPC9zdHJvbmc+IQ=3D=3D
""")
        mailhost = self._makeOne('MailHost')
        mailhost.send(msg)
        out = parse_message(mailhost.sent)
        self.assertEqual(out.as_string(), msg.as_string())

        # we can even alter a from and subject headers without affecting the
        # original object
        mailhost.send(msg,
                      mfrom='Foo Bar <foo@example.com>', subject='Changed!')
        out = parse_message(mailhost.sent)

        # We need to make sure we didn't mutate the message we were passed
        self.assertNotEqual(out.as_string(), msg.as_string())
        self.assertEqual(out['From'], 'Foo Bar <foo@example.com>')
        self.assertEqual(
            msg['From'],
            '=?utf-8?q?Jos=C3=A9_Andr=C3=A9s?= <jose@example.com>')
        # The subject is encoded with the body encoding since no
        # explicit encoding was specified
        self.assertEqual(out['Subject'], '=?utf-8?q?Changed!?=')
        self.assertEqual(msg['Subject'],
                         '=?utf-8?q?=C2=BFEsferificaci=C3=B3n=3F?=')

    def testSendMultipartMessageObject(self):
        TO = 'Name, Nick <recipient@example.com>'
        FROM = 'sender@example.com'

        outer = MIMEMultipart()
        outer['Subject'] = 'This is the subject'
        outer['To'] = TO
        outer['From'] = FROM
        outer.preamble = 'This is a MIME encoded multipart message.\n'
        outer.epilogue = ''
        body = 'This is the message body.'
        msg = MIMEText(body, _subtype='text', _charset='utf-8')
        outer.attach(msg)
        outer.set_boundary('===============8011890429167670482==')

        mailhost = self._makeOne('MailHost')
        mailhost.send(
            outer.as_string(),
            mto=TO,
            mfrom=FROM,
        )
        # date_pattern matches e.g. `Tue, 21 Jul 2020 08:50:04 +0200`
        date_pattern = (
            b'[a-zA-Z]{2,3}, [0-9]{1,2} [a-zA-Z]{3} [0-9]{4}'
            b' [0-9]{2}:[0-9]{2}:[0-9]{2} [+-]{1}[0-9]{4}')
        pattern = (
            b'Content-Type: multipart/mixed; '
            b'boundary="===============8011890429167670482=="\n'
            b'MIME-Version: 1.0\n'
            b'Subject: This is the subject\n'
            b'To: Name, Nick <recipient@example.com>\n'
            b'From: sender@example.com\n'
            b'Date: %s\n\n'
            b'This is a MIME encoded multipart message.\n\n'
            b'--===============8011890429167670482==\n'
            b'Content-Type: text/text; charset="utf-8"\n'
            b'MIME-Version: 1.0\n'
            b'Content-Transfer-Encoding: quoted-printable\n\n'
            b'This is the message body.\n'
            b'--===============8011890429167670482==--\n'
            % date_pattern)
        if six.PY2:
            self.assertRegexpMatches(mailhost.sent, pattern)
        else:  # PY3
            pattern = pattern.replace(b"\n", b"\r\n")
            self.assertRegex(mailhost.sent, pattern)

    def testExplicitBase64Encoding(self):
        mailhost = self._makeOne('MailHost')
        mailhost.send('Date: Sun, 27 Aug 2006 17:00:00 +0200\n\nA Message',
                      mfrom='sender@example.com',
                      mto='Foo Bar <foo@example.com>', encode='base64')
        # Explicitly stripping the output here since the base64 encoder
        # in Python 3 adds a line break at the end.
        outmsg = b"""\
Date: Sun, 27 Aug 2006 17:00:00 +0200
Subject: [No Subject]
To: Foo Bar <foo@example.com>
From: sender@example.com
Content-Transfer-Encoding: base64
Mime-Version: 1.0

QSBNZXNzYWdl"""

        if six.PY3:
            outmsg = outmsg.replace(b"\n", b"\r\n")

        self.assertEqual(mailhost.sent.strip(), outmsg)

    def testExplicit7bitEncoding(self):
        mailhost = self._makeOne('MailHost')
        mailhost.send('Date: Sun, 27 Aug 2006 17:00:00 +0200\n\nA Message',
                      mfrom='sender@example.com',
                      mto='Foo Bar <foo@example.com>', encode='7bit')

        outmsg = b"""\
Date: Sun, 27 Aug 2006 17:00:00 +0200
Subject: [No Subject]
To: Foo Bar <foo@example.com>
From: sender@example.com
Content-Transfer-Encoding: 7bit
Mime-Version: 1.0

A Message"""

        if six.PY3:
            outmsg = outmsg.replace(b"\n", b"\r\n")

        self.assertEqual(mailhost.sent, outmsg)

    @unittest.skipUnless(PY36, 'requires Python 3.6+')
    def testExplicit8bitEncoding(self):
        mailhost = self._makeOne('MailHost')
        # We pass an encoded string with unspecified charset, it should be
        # encoded 8bit
        mailhost.send('Date: Sun, 27 Aug 2006 17:00:00 +0200\n\n'
                      'A M\xc3\xa9ssage',
                      mfrom='sender@example.com',
                      mto='Foo Bar <foo@example.com>', encode='8bit')
        msg = mailhost.sent
        if six.PY3:
            msg = msg.decode()
        self.assertEqual(msg, """\
Date: Sun, 27 Aug 2006 17:00:00 +0200
Subject: [No Subject]
To: Foo Bar <foo@example.com>
From: sender@example.com
Content-Transfer-Encoding: 8bit
Mime-Version: 1.0

A M\xc3\xa9ssage""".replace("\n", "\r\n"))

    def testSendTemplate(self):
        content = FakeContent('my_template', 'A Message')
        mailhost = self._makeOne('MailHost')
        result = mailhost.sendTemplate(content, 'my_template',
                                       mto='Foo Bar <foo@example.com>',
                                       mfrom='sender@example.com')
        self.assertEqual(result, 'SEND OK')
        result = mailhost.sendTemplate(content, 'my_template',
                                       mto='Foo Bar <foo@example.com>',
                                       mfrom='sender@example.com',
                                       statusTemplate='wrong_name')
        self.assertEqual(result, 'SEND OK')
        result = mailhost.sendTemplate(content, 'my_template',
                                       mto='Foo Bar <foo@example.com>',
                                       mfrom='sender@example.com',
                                       statusTemplate='check_status')
        self.assertEqual(result, 'Message Sent')

    def testSendMultiPartAlternativeMessage(self):
        msg = ("""\
Content-Type: multipart/alternative; boundary="===============0490954888=="
MIME-Version: 1.0
Date: Sun, 27 Aug 2006 17:00:00 +0200
Subject: My multipart email
To: Foo Bar <foo@example.com>
From: sender@example.com

--===============0490954888==
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: quoted-printable

This is plain text.

--===============0490954888==
Content-Type: multipart/related; boundary="===============2078950065=="
MIME-Version: 1.0

--===============2078950065==
Content-Type: text/html; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: quoted-printable

<p>This is html.</p>
--===============2078950065==--
--===============0490954888==--
""")

        mailhost = self._makeOne('MailHost')
        # Specifying a charset for the header may have unwanted side
        # effects in the case of multipart mails.
        # (TypeError: expected string or buffer)
        mailhost.send(msg, charset='utf-8')
        # There is a one newline difference in the output between
        # zope.sendmail versions.
        if six.PY3:
            msg = msg.encode().replace(b"\n", b"\r\n")
        self.assertEqual(mailhost.sent[:677], msg[:677])

        if six.PY2:
            self.assertTrue(mailhost.sent.endswith(b'==0490954888==--\n'))
        else:  # PY3
            self.assertTrue(mailhost.sent.endswith(b'==0490954888==--\r\n'))

    def testSendMultiPartMixedMessage(self):
        msg = ("""\
Content-Type: multipart/mixed; boundary="XOIedfhf+7KOe/yw"
Content-Disposition: inline
MIME-Version: 1.0
Date: Sun, 27 Aug 2006 17:00:00 +0200
Subject: My multipart email
To: Foo Bar <foo@example.com>
From: sender@example.com

--XOIedfhf+7KOe/yw
Content-Type: text/plain; charset=us-ascii
Content-Disposition: inline

This is a test with as attachment OFS/www/new.gif.

--XOIedfhf+7KOe/yw
Content-Type: image/gif
Content-Disposition: attachment; filename="new.gif"
Content-Transfer-Encoding: base64

R0lGODlhCwAQAPcAAP8A/wAAAFBQUICAgMDAwP8AAIAAQAAAoABAgIAAgEAAQP//AP//gACA
gECAgP///wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAEAAAAALAAAAAALABAAAAg7AAEIFKhgoEGC
CwoeRKhwoYKEBhVIfLgg4UQAFCtqbJixYkOEHg9SHDmQJEmMEBkS/IiR5cKXMGPKDAgAOw==

--XOIedfhf+7KOe/yw
Content-Type: text/plain; charset=iso-8859-1
Content-Disposition: attachment; filename="test.txt"
Content-Transfer-Encoding: quoted-printable

D=EDt =EFs =E9=E9n test

--XOIedfhf+7KOe/yw--
""")

        mailhost = self._makeOne('MailHost')
        # Specifying a charset for the header may have unwanted side
        # effects in the case of multipart mails.
        # (TypeError: expected string or buffer)
        mailhost.send(msg, charset='utf-8')
        if six.PY3:
            msg = msg.encode().replace(b"\n", b"\r\n")
        self.assertEqual(mailhost.sent, msg)

    def test_manage_makeChanges(self):
        mailhost = self._makeOne('MailHost')

        mailhost.manage_makeChanges(
            title='MailHost',
            smtp_host='localhost',
            smtp_port='25',
        )
        self.assertEqual(mailhost.title, 'MailHost')
        self.assertEqual(mailhost.smtp_host, 'localhost')
        self.assertEqual(mailhost.smtp_port, 25)


class QueueingDummyMailHost(MailHost):
    """Dummy mail host implementation which supports queueing."""

    meta_type = 'Queueing Dummy Mail Host'

    def __init__(self, id, smtp_queue_directory):
        self.id = id
        self.smtp_queue = True
        self.smtp_queue_directory = smtp_queue_directory
        self.started_queue_processor_thread = False

    def _startQueueProcessorThread(self):
        self.started_queue_processor_thread = True


class TestMailHostQueuing(unittest.TestCase):

    smtp_queue_directory = None

    def _getTargetClass(self):
        return QueueingDummyMailHost

    def _makeOne(self, *args):
        self.tmpdir = tempfile.mkdtemp(suffix='MailHostTests')
        self.smtp_queue_directory = os.path.join(self.tmpdir, 'queue')
        return self._getTargetClass()(
            *args, smtp_queue_directory=self.smtp_queue_directory)

    def _callFUT(self):
        mh = self._makeOne('MailHost')
        mh.send(
            'Nice to see you!',
            mto='user@example.com',
            mfrom='zope@example.com',
            subject='Hello world')
        transaction.commit()
        return mh

    def tearDown(self):
        super(TestMailHostQueuing, self).tearDown()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def testStartQueueProcessorThread(self):
        mh = self._callFUT()
        self.assertTrue(mh.started_queue_processor_thread)
        md = zope.sendmail.maildir.Maildir(self.smtp_queue_directory)
        self.assertEqual(len(list(md)), 1)

    @unittest.skipUnless(PY36, 'requires Python 3.6+')
    def test_8bit_special(self):
        mh = self._makeOne('MailHost')
        mh.send(u"""\
Mime-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit

\u00e4
""",
                mto='user@example.com',
                mfrom='zope@example.com',
                subject='Hello world',
                charset='utf-8')
        transaction.commit()
        self.assertTrue(mh.started_queue_processor_thread)
        md = zope.sendmail.maildir.Maildir(self.smtp_queue_directory)
        self.assertEqual(len(list(md)), 1)

    def testNotStartQueueProcessorThread(self):
        os.environ['MAILHOST_QUEUE_ONLY'] = '1'
        try:
            mh = self._callFUT()
        finally:
            del os.environ['MAILHOST_QUEUE_ONLY']
        self.assertFalse(mh.started_queue_processor_thread)
        md = zope.sendmail.maildir.Maildir(self.smtp_queue_directory)
        self.assertEqual(len(list(md)), 1)
