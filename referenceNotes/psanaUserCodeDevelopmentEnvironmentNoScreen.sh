#!/bin/bash


#gnome-terminal -e "bash -c \"echo foo; echo bar; exec bash\""
gnome-terminal -e "bash -c \"ssh psana; cd softXRayDataAndControls/myAnalysisTools/pyqtgraphBuildingBlocks; ipython\""
