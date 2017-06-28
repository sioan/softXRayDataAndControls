from pcaspy import SimpleServer, Driver

class myDriver(Driver):
    def __init__(self):
        super(myDriver, self).__init__()

prefix = 'SXR:MCP:'
pvdb = {
	'FIRST:AMPLITUDE' : {
	'prec' : 3,
	},
	'SECOND:AMPLITUDE' : {
	'prec' : 3,
	},
	'FIRST:DELAY' : {
	'prec' : 3,
	},
	'SECOND:DELAY' : {
	'prec' : 3,
	},
}

if __name__ == '__main__':
	server = SimpleServer()
	server.createPV(prefix, pvdb)
	driver = myDriver()

	while True:
		# process CA transactions
		server.process(0.1)
