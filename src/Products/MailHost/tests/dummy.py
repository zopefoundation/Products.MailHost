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
""" Helpers for MailHost unit tests.
"""
from Products.MailHost.MailHost import MailHost


class DummyMailHost(MailHost):
    meta_type = 'Dummy Mail Host'

    def __init__(self, id):
        self.id = id
        self.sent = ''

    def _send(self, mfrom, mto, messageText, immediate=False):
        self.sent = messageText
        self.immediate = immediate


class FakeContent:

    def __init__(self, template_name, message):

        def template(self, context, REQUEST=None):
            return message
        setattr(self, template_name, template)

    @staticmethod
    def check_status(context, REQUEST=None):
        return 'Message Sent'
