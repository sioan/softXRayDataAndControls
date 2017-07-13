import re
import zmq
import logging
import argparse
import threading
from psp import Pv
from data import Trace
from pcaspy import SimpleServer, Driver


LOG = logging.getLogger('acq_ioc')


class AcqDriver(Driver):
    def __init__(self, prefix, pvdb, port):
        super(AcqDriver, self).__init__()
        self.run = True
        self.name_re = re.compile("%s(?P<name>.*)"%prefix)
        self.prefix = prefix
        self.pvdb = pvdb
        self.zmq_port = port
        self.ctx = zmq.Context()
        self.sock = self.ctx.socket(zmq.PULL)
        self.sock.bind('tcp://*:%d'%self.zmq_port)
        self.zmq_thread = threading.Thread(target = self.runZMQ)
        self.zmq_thread.daemon = True
        self.zmq_thread.start()

    def runZMQ(self):
        while self.run:
            data = self.sock.recv_pyobj()
            match = self.name_re.match(data.name)
            if match:
                base = match.group('name')
                waveform = '%s:TRACE'%base
                scale = '%s:SCALE'%base
                if waveform in self.pvdb and scale in self.pvdb:
                    self.setParam(waveform, data.data[:self.pvdb[waveform]['count']])
                    self.setParam(scale, data.scale)
                    self.updatePVs()
                else:
                    LOG.warn("Unrecognized PV recieved: %s", base)
            else:
                LOG.warn("Invalid PV - does not match prefix: %s", data.name)


def _check_prefix(prefix):
    if prefix is None:
        return prefix
    else:
        if prefix.endswith(':'):
            return prefix
        else:
            return prefix + ':'


def main(prefix, pvdb, port):
    LOG.info('Starting ACQ ioc, abort with Ctrl-C')
    server = SimpleServer()
    server.createPV(_check_prefix(prefix), pvdb)
    driver = AcqDriver(_check_prefix(prefix), pvdb, port)
    myString = "pvdb = "+str(pvdb)
    #print myString 
    LOG.debug('ACQ IOC is now started')
    try:
        # Run the driver process loop
        while driver.run:
            try:
                # process CA transactions
                server.process(0.1)
            except KeyboardInterrupt:
                LOG.info('ACQ IOC stopped by console interrupt!')
                driver.run = False
    finally:
        pass
        

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description='Simple python IOC for broadcasting ')
        parser.add_argument(
            '-p',
            '--port',
            type=int,
            default=12301,
            help='the port to listen for data on'
        )

        parser.add_argument(
            '--log-level',
            metavar='LOG_LEVEL',
            default='INFO',
            help='the logging level of the client (default INFO)'
        )

        parser.add_argument(
            'prefix',
            metavar='PV_PREFIX',
            help='the PV prefix to use for the IOC'
        )

        parser.add_argument(
            'detectors',
            nargs='+',
            help='acq to export as PVs. format is PV_NAME,ARRAY_SIZE'
        )

        args = parser.parse_args()

        pvdb = {}
        log_level = getattr(logging, args.log_level.upper(), logging.INFO)
        logging.basicConfig(format='[ %(asctime)s | %(levelname)-8s] %(message)s', level=log_level)

        # add pvs to db
        for det in args.detectors:
            try:
                name, count = det.split(',')
                pvdb["%s:TRACE"%name] = { 'type': 'float', 'count' : int(count) }
                pvdb["%s:SCALE"%name] = { 'type': 'float' }
            except:
                LOG.error("Invalid detector id string: %s", det)

        main(args.prefix, pvdb, args.port)
    except KeyboardInterrupt:
        pass
