import os, sys
sys.path.append(os.getcwd()+'/../')
sys.path.append(os.getcwd()+'/../ens')
sys.path.append(os.getcwd()+'/../tests')

from ens.helper.MPC import MPC

from ens.computation.calc_ENS import *

if __name__=='__main__':
    # initialization
    clearc
    mpc_obj = MPC(os.path.join('cases/case33bw'))

    livebus_loc = [1, 18, 22, 25, 33]
    livebus_auto = [1, 1, 0, 0, 0]

    sw_recloser = [1, 7]  # %branch number of Reclousers
    sw_sectionalizer = []  # #    %branch number of Sectionalizers
    sw_automatic_sectioner = []  # %branch number and Automatic
    sw_manual_sectioner = [6, 5]
    sw_cutout = []  # %Location and Automatic (1)/Manual (0) disconnector switches
    current_xy = [-10, -10]  # %The current location of maintenance group
    speed = 50

    Total_ENS = calc_ENS(mpc_obj, sw_recloser, sw_sectionalizer, sw_automatic_sectioner, sw_manual_sectioner, sw_cutout,
                         livebus_loc, livebus_auto, current_xy, speed)

    print(Total_ENS)