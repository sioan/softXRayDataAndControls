sxrIpimbs = {
    'ipm1': {'base': 'SXR:DG1:IMB:01',
             'ioc':  'SXR:R04:IOC:34',
             'evr':  'SXR:R04:EVR:34'
             },
    'pim1': {'base': 'SXR:DG1:IMB:02',
             'ioc':  'SXR:R04:IOC:34',
             'evr':  'SXR:R04:EVR:34'
             },
    'ipm2': {'base': 'HFX:DG2:IMB:01',
             'ioc':  'SXR:R38:IOC:43',
             'evr':  'SXR:R38:EVR:43'
             },
    'pim2': {'base': 'HFX:DG2:IMB:02',
             'ioc':  'SXR:R38:IOC:43',
             'evr':  'SXR:R38:EVR:43'
             },
    'diomono': {'base': 'HFX:MON:IMB:01',
                'ioc':  'SXR:R38:IOC:43',
                'evr':  'SXR:R38:EVR:43'
                },
    'decmono': {'base': 'HFX:MON:IMB:02',
                'ioc':  'SXR:R38:IOC:43',
                'evr':  'SXR:R38:EVR:43'
                },
    'ipmmono': {'base': 'HFX:MON:IMB:03',
                'ioc':  'SXR:R38:IOC:43',
                'evr':  'SXR:R38:EVR:43'
                },
    'pim3m': {'base': 'HFX:DG3:IMB:02',
              'ioc':  'SXR:R38:IOC:43',
              'evr':  'SXR:R38:EVR:43'
              },
    'ipm3': {'base': 'HFX:DG3:IMB:03',
             'ioc':  'SXR:R38:IOC:43',
             'evr':  'SXR:R38:EVR:43'
             },
    'pim3': {'base': 'SXR:DG3:IMB:04',
             'ioc':  'SXR:R38:IOC:43',
             'evr':  'SXR:R38:EVR:43'
             }
    }


def getpvbase(ipimb):
    return sxrIpimbs[ipimb]['base']

def getioc(ipimb):
    return sxrIpimbs[ipimb]['ioc']

def getevr(ipimb):
    return sxrIpimbs[ipimb]['evr']

class Ipimb(object):
    def __init__(self,name):
        object.__init__(self)
        self.pvbase = getpvbase(name)
        self.ioc = getioc(name)
        self.evr = getevr(name)
        pass

    def __repr__(self):
        return self.status()

    def status(self):
        stat = ""
        return stat

    def ioc_restart(self):
        pypsepics.put("%s:SYSRESET" % self.ioc, 1)
        pass

    pass
