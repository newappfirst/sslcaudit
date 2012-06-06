# ----------------------------------------------------------------------
# SSLCAUDIT - a tool for automating security audit of SSL clients
# Released under terms of GPLv3, see COPYING.TXT
# Copyright (C) 2012 Alexandre Bezroutchko abb@gremwell.com
# ----------------------------------------------------------------------

import logging, unittest

from sslcaudit.modules.sslcert.ProfileFactory import DEFAULT_CN, SSLProfileSpec_SelfSigned, SSLProfileSpec_IMCA_Signed, SSLProfileSpec_Signed, IM_CA_FALSE_CN, IM_CA_TRUE_CN, IM_CA_NONE_CN, SSLProfileSpec_UserSupplied
from sslcaudit.modules.sslcert.SSLServerHandler import     UNEXPECTED_EOF, ALERT_UNKNOWN_CA, ConnectedGotEOFBeforeTimeout, ConnectedGotRequest
from sslcaudit.modules.sslproto.ProfileFactory import SSLServerProtoSpec
from sslcaudit.test.ExternalCommandHammer import CurlHammer
from sslcaudit.test.TCPConnectionHammer import TCPConnectionHammer
from sslcaudit.test.TestConfig import *
from test import TestModule
from test.TestModule import ECCAR, mk_sslcaudit_argv

LOCALHOST = 'localhost'
HAMMER_HELLO = 'hello'

ALERT_NO_SHARED_CIPHER = 'no shared cipher'

class TestSSLProtoModule(TestModule.TestModule):
    '''
    Unittests for SSLCert.
    '''
    logger = logging.getLogger('TestSSLProtoModule')


    def test_plain_tcp_client(self):
        # Plain TCP client causes unexpected UNEXPECTED_EOF.
        eccars = []
        for proto in ('sslv23',):
            for cipher in ('HIGH', 'MEDIUM', 'LOW', 'EXPORT'):
                eccars.append(ECCAR(SSLServerProtoSpec(proto, cipher), UNEXPECTED_EOF))

        self._main_test(
            ['-m', 'sslproto'],
            TCPConnectionHammer(len(eccars)),
            eccars
        )

    def test_curl(self):
        # curl (and any other proper SSL client for that purpose) is expected to reject SSLv2 and weak ciphers
        eccars = []
        for proto in ('sslv23',):
            for cipher in ('HIGH', 'MEDIUM', 'LOW', 'EXPORT'):
                if cipher == 'HIGH' or cipher == 'MEDIUM':
                    expected_res = ALERT_UNKNOWN_CA
                else:
                    expected_res = ALERT_NO_SHARED_CIPHER
                eccars.append(ECCAR(SSLServerProtoSpec(proto, cipher), expected_res=expected_res))

        self._main_test(
            ['-m', 'sslproto'],
            CurlHammer(len(eccars)),
            eccars
        )

if __name__ == '__main__':
    TestModule.init_logging()
    unittest.main()
