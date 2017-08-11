#!/bin/bash
screen -d -m -S psanaDevelopmentIPythonTerminal
screen -S psanaDevelopmentIPythonTerminal -X stuff 'ssh psana \n'
screen -S psanaDevelopmentIPythonTerminal -X stuff 'cd softXRayDataAndControls/myAnalysisTools/pyqtgraphBuildingBlocks \n'
screen -S psanaDevelopmentIPythonTerminal -X stuff 'ipython \n'
gnome-terminal -e screen -r psanaDevelopmentIPythonTerminal
