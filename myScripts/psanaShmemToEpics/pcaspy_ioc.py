from pcaspy import SimpleServer, Driver

class myDriver(Driver):
    def __init__(self):
        super(myDriver, self).__init__()

prefix = 'SXR:NOTE:'
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
