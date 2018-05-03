import argparse
from psana import *


def main(exp, run):
    ds = DataSource('exp=%s:run=%d:smd'%(exp, run))

    env = ds.env()
    configs = env.configStore()

    cntrl = configs.get(ControlData.ConfigV3)

    """
        The ControlDataV3 has the following data bits in it
        'duration', 'events', 'npvControls', 'npvLabels', 'npvMonitors', 'pvControls', 'pvLabels', 'pvMonitors', 'uses_duration', 'uses_events', 'uses_l3t_events'
    """
    output  = "uses_duration: %d\tduration: (%s)\n"%(cntrl.uses_duration(), cntrl.duration())
    output += "uses_events:   %d\tevents:   %s\n"%(cntrl.uses_events(), cntrl.events())
    output += "uses_l3t:      %d\n"%cntrl.uses_l3t_events()
    output += "npvControls:   %d\n"%cntrl.npvControls()
    for pvcntrls in cntrl.pvControls():
        output += "  %s: %.f\n"%(pvcntrls.name(), pvcntrls.value())
    output += "npvMonitors:   %d\n"%cntrl.npvMonitors()
    for pvmonitors in cntrl.pvMonitors():
        output += "  %s: %.f\n"%(pvmonitors.name(), pvmonitors.value())
    output += "npvLabels:     %d\n"%cntrl.npvLabels()
    for pvlabels in cntrl.pvLabels():
        output += "  %s: %s\n"%(pvlabels.name(), pvlabels.value())

    print output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Dump the control data from the config of a run'
    )

    parser.add_argument(
        'exp',
        metavar='EXP',
        help='the experiment number'
    )

    parser.add_argument(
        'run',
        metavar='RUN',
        type=int,
        help='the run number'
    )

    args = parser.parse_args()

    try:
      main(args.exp, args.run)
    except KeyboardInterrupt:
      pass
