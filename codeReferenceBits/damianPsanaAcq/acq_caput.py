import zmq
import argparse
from psp import Pv
from data import Trace

def main(port, limit):
    pvs = {}

    ctx = zmq.Context()
    sock = ctx.socket(zmq.PULL)
    sock.bind('tcp://*:%d'%port)

    while True:
        data = sock.recv_pyobj()
        if data.name not in pvs:
            pvs[data.name] = Pv.Pv(data.name)
            pvs[data.name].use_numpy = True
        pvs[data.name].put(data.data[:limit])

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description='Send acqiris traces to epics via pyca')
        parser.add_argument(
            '-p',
            '--port',
            type=int,
            default=12301,
            help='port to listen for data on'
        )

        parser.add_argument(
            '-l',
            '--limit',
            type=int,
            default=500,
            help='the maximum size of the epics waveform pv we are pushing to'
        )

        args = parser.parse_args()

        main(args.port, args.limit)
    except KeyboardInterrupt:
        pass
