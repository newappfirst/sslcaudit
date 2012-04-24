from threading import Thread
import unittest, time
import logging
from socket import socket
from src.ClientAuditor.ClientAuditorServer import ClientAuditorServer
from src.ClientAuditor.ClientConnectionAuditResult import ClientConnectionAuditResultEnd, ClientConnectionAuditResultStart, ClientConnectionAuditResult
from src.ClientAuditor.ClientHandler import ClientAuditResult
from src.ClientAuditor.Dummy.DummyClientAuditorSet import DummyClientAuditorSet

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('PlainTcpClient').setLevel(logging.INFO)
#logging.getLogger('TestClientAuditorServer').setLevel(logging.INFO)

TEST_HOST = 'localhost'
TEST_PORT = 9999

class PlainTcpClient(Thread):
    '''
    This class continuously tries to connect to the specified host and port.
    After connection is established, it immediately closes it.
    '''
    logger = logging.getLogger('PlainTcpClient')
    RECONNECT_ATTEMPTS = 5
    RECONNECT_DELAY = 1

    def __init__(self, peer):
        Thread.__init__(self, target=self.run)
        self.peer = peer
        self.daemon = True
        self.should_stop = False

    def run(self):
        self.logger.debug("running %s", self)
        for _ in range(self.RECONNECT_ATTEMPTS):
            if self.should_stop: break
            self.connect()
            time.sleep(self.RECONNECT_DELAY)
        self.logger.debug("exiting %s", self)

    def connect(self):
        self.logger.debug("connecting to %s", self.peer)
        s = socket()
        s.connect(self.peer)
        s.close()

    def stop(self):
        self.logger.debug("stopping %s", self)
        self.should_stop = True


class TestClientAuditorServer(unittest.TestCase):
    '''
    This class tests ClientAuditorServer.
    '''
    GETRESULT_TIMEOUT = 5
    logger = logging.getLogger('TestClientAuditorServer')

    def test(self):
        auditor_set = DummyClientAuditorSet()
        server = ClientAuditorServer((TEST_HOST, TEST_PORT), auditor_set)
        server.start()
        self.logger.debug('ClientAuditorServer started')

        plain_tcp_client = PlainTcpClient((TEST_HOST, TEST_PORT))
        plain_tcp_client.start()
        self.logger.debug('PlainTCPClient started')

        got_result_start = 0
        got_result = 0
        got_result_end = 0
        got_bulk_result = 0
        while not (got_result_start == 1 and got_result == auditor_set.len() and got_result_end == 1 and got_bulk_result == 1):
            self.logger.debug('waiting for a result from the queue ...')
            res = server.res_queue.get(timeout=self.GETRESULT_TIMEOUT)
            self.logger.debug('got a result %s', res)

            if isinstance(res, ClientConnectionAuditResultStart):
                got_result_start = got_result_start + 1
            elif isinstance(res, ClientConnectionAuditResultEnd):
                got_result_end = got_result_end + 1
            elif isinstance(res, ClientConnectionAuditResult):
                got_result = got_result + 1
            elif isinstance(res, ClientAuditResult):
                got_bulk_result = got_bulk_result + 1

        plain_tcp_client.stop()

if __name__ == '__main__':
    unittest.main()