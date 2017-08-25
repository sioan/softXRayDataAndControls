from pcaspy import SimpleServer, Driver

class myDriver(Driver):
    def __init__(self):
        super(myDriver, self).__init__()

prefix = 'DAQ:SXR:MON:ACQ13:'
pvdb = {
    'RAND' : {
        'prec' : 3,
    },
    'Waveform' : { 'count': 60000,
                                'prec' : 5 },
}

if __name__ == '__main__':
	server = SimpleServer()
	server.createPV(prefix, pvdb)
	driver = myDriver()

	while True:
		# process CA transactions
		server.process(0.1)
