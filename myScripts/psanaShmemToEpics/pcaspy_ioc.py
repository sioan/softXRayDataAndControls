from pcaspy import SimpleServer, Driver
import argparse
import sys

class myDriver(Driver):
    def __init__(self):
        super(myDriver, self).__init__()

parser = argparse.ArgumentParser(description='PCASpy Server holding notebook waveform (array) PV. Run on hutch control or IOC node.')
parser.add_argument('hutch', metavar='HUTCH', help='Name of hutch (AMO or SXR)')
try:
	args=parser.parse_args()
except:
	pass #Likely no arguments passed in
if args.hutch.lower() == "amo":
	prefix = "AMO:NOTE:"
elif args.hutch.lower() == "sxr":
	prefix = "SXR:NOTE:"
else:
	print "Error, hutch %s not supported!" % args.hutch
        sys.exit()

pvdb = {
    'RAND' : {
        'prec' : 3,
    },
    'ARRAYB:01' : { 'count': 2000,
                                'prec' : 5 },
}

if __name__ == '__main__':
	server = SimpleServer()
	server.createPV(prefix, pvdb)
	driver = myDriver()

	while True:
		# process CA transactions
		server.process(0.1)
