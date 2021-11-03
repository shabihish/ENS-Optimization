import os, sys

import numpy as np

sys.path.append(os.getcwd() + '/../')
sys.path.append(os.getcwd() + '/../ens')
sys.path.append(os.getcwd() + '/../tests')

from ens.helper.MPC import MPC

from ens.computation.calc_ENS import *

if __name__ == '__main__':
    # initialization
    clearc()
    mpc_obj = MPC(os.path.join('cases/case33bw'))

    livebus_loc = [1, 18, 22, 25, 33]
    livebus_auto = [1, 1, 0, 0, 0]

    sw_recloser = np.array(
        [[1, 7], [1, 6], [1, 6], [1, 6], [1, 6], [1, 6], [1, 6], [1, 6], [1, 6], [1, 6], [1, 6], [1, 6], [1, 6],
         [1, 6]])
    sw_sectionalizer = np.array([[], [], [], [], [], [], [], [], [], [], [], [], [], []])
    sw_automatic_sectioner = np.array([[], [], [], [], [], [], [], [], [], [], [], [], [], []])
    sw_manual_sectioner = np.array(
        [[6, 5], [4, 5], [4, 5], [4, 5], [4, 5], [4, 5], [4, 5], [4, 5], [4, 5], [4, 5], [4, 5], [4, 5], [4, 5],
         [4, 5]])
    sw_cutout = np.array([[], [], [], [], [], [], [], [], [], [], [], [], [], []])
    current_xy = [-10, -10]
    speed = 50

    livebus_loc = np.array([livebus_loc])
    livebus_loc = np.r_[
        livebus_loc, livebus_loc, livebus_loc, livebus_loc, livebus_loc, livebus_loc, livebus_loc, livebus_loc, livebus_loc, livebus_loc, livebus_loc, livebus_loc, livebus_loc, livebus_loc]

    livebus_auto = np.array([livebus_auto])
    livebus_auto = np.r_[
        livebus_auto, livebus_auto, livebus_auto, livebus_auto, livebus_auto, livebus_auto, livebus_auto, livebus_auto, livebus_auto, livebus_auto, livebus_auto, livebus_auto, livebus_auto, livebus_auto]

    current_xy = np.array([current_xy])
    current_xy = np.r_[current_xy]

    Total_ENS = calc_ENS(mpc_obj, sw_recloser, sw_sectionalizer, sw_automatic_sectioner, sw_manual_sectioner, sw_cutout,
                         livebus_loc, livebus_auto, current_xy, speed)

    print('Total calculated ENS: {}'.format(Total_ENS))
