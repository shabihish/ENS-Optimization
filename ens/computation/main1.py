import os, sys

import numpy as np

sys.path.append(os.getcwd()+'/../')
sys.path.append(os.getcwd()+'/../ens')
sys.path.append(os.getcwd()+'/../tests')

from ens.helper.MPC import MPC

from ens.computation.calc_ENS import *

if __name__=='__main__':
    # initialization
    clearc
    mpc_obj = MPC(os.path.join('cases/case33bw'))

    nc_sw = np.array([1,2,3,7])
    mpc_obj.branch.iloc[nc_sw - 1, 10] = 0
    nbus = mpc_obj.bus.shape[0]
    nbranch = mpc_obj.branch.shape[0]
    for i in range(3000):
        mgdefinition(mpc_obj, nc_sw, nbus, nbranch)