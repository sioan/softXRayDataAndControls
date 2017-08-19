#need to source  and $PSPKG_ROOT/etc/set_env.sh

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


