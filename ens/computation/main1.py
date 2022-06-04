import os, sys
os.system("taskset -p 0xff %d" % os.getpid())


import numpy as np

sys.path.append(os.getcwd() + '/../')
sys.path.append(os.getcwd() + '/../ens')
sys.path.append(os.getcwd() + '/../tests')

from ens.helper.MPC import MPC

from ens.computation.calc_ENS import *

# initialization
clearc()
mpc_obj = MPC(os.path.join('data/case33bw'))

N = 10000
print(np.show_config())

livebus_loc = [1, 18, 22, 25, 33]
livebus_auto = [1, 1, 0, 0, 0]

sw_recloser = np.repeat([[1, 7]], N, axis=0)
sw_sectionalizer = np.repeat([[]], N, axis=0)
sw_automatic_sectioner = np.repeat([[]], N, axis=0)
sw_manual_sectioner = np.repeat([[6, 5]], N, axis=0)
sw_cutout = np.repeat([[]], N, axis=0)
current_xy = [-10, -10]
speed = 50

livebus_loc = np.repeat([livebus_loc], N, axis=0)

livebus_auto = np.repeat([livebus_auto], N, axis=0)

current_xy = np.array([current_xy])
current_xy = np.r_[current_xy]

Total_ENS = calc_ENS(mpc_obj, sw_recloser, sw_sectionalizer, sw_automatic_sectioner, sw_manual_sectioner, sw_cutout,
                     livebus_loc, livebus_auto, current_xy, speed)

print(Total_ENS)
