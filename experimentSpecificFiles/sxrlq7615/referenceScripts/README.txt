instructions for running mcp driver
on psana run 
mpirun -n 2 python MCP_driver.py -r 100 -n 1000

on another computer run 

psplot -s <machine name> -p 12301 TRACE AMPLITUDES
