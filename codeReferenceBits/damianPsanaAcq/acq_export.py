import zmq
import argparse
from data import Trace
from psana import *


def main(exp, run, online, host, port, *detnames):
    if online:
        expname = "shmem=psana.0:stop=no"
    else:
        expname = "exp=%s:run=%d"%(exp, run)

    ctx =zmq.Context()
    sock = ctx.socket(zmq.PUSH)
    sock.connect("tcp://%s:%d"%(host,port))

    ds = DataSource(expname)
    print "priting first detnames"
    print detnames
    detnames = [ detstr.split(',') for detstr in detnames ]
    print "printing detnames"
    print detnames
    #dets = [ (pv,Detector(name),int(ch)) for pv,name,ch in detnames ]
    dets = [(detnames[0][0],Detector(detnames[1][0]),int(detnames[2][0]))]
    # remove if it is not an aqiris
    dets = filter(lambda x: x[1].dettype == 16, dets)

    for evt in ds.events():
        for pv, det, ch in dets:
            waveforms = det.waveform(evt)
            times = det.wftime(evt)
            sock.send_pyobj(Trace(pv, times[ch][1] - times[ch][0], waveforms[ch]))


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description='Process acqiris traces')
        parser.add_argument(
            '-e',
            '--exp',
            help='the experiment name'
        )

        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '-o',
            '--online',
            action='store_true',
            help='run from shared memory'
        )
        group.add_argument(
            '-r',
            '--run',
            type=int,
            help='the run number to use when running offline'
        )

        parser.add_argument(
            '-H',
            '--host',
            default='localhost',
            help='hostname to push data to'
        )

        parser.add_argument(
            '-p',
            '--port',
            type=int,
            default=12301,
            help='port to push data to'
        )

        parser.add_argument(
            'detectors',
            nargs='+',
            help='acq to export. format is PV,DAQ_NAME,CHANNEL'
        )

        args = parser.parse_args()

        main(args.exp, args.run, args.online, args.host, args.port, *args.detectors)
    except KeyboardInterrupt:
        pass
