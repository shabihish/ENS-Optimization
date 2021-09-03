import numpy as np

from ens.helper.MPC import MPC
from ens.computation.calc_ENS import *
import os, pytest


@pytest.fixture
def mpc():
    return MPC(os.path.join('cases/case33bw'))


def test_calc_ENS(mpc):
    livebus_loc = np.array([[1, 18, 22, 25, 33], [1, 18, 22, 25, 33]])
    livebus_auto = np.array([[1, 1, 0, 0, 0], [1, 1, 0, 0, 0]])
    sw_recloser = np.array([[1, 7], [1, 7]])
    sw_sectionalizer = np.array([[], []])
    sw_automatic_sectioner = np.array([[], []])
    sw_manual_sectioner = np.array([[6, 5], [6, 5]])
    sw_cutout = np.array([[], []])
    current_xy = np.array([[-10, -10], [-10, -10]])
    speed = 50

    tot_ENS = calc_ENS(mpc, sw_recloser, sw_sectionalizer, sw_automatic_sectioner, sw_manual_sectioner, sw_cutout,
                       livebus_loc, livebus_auto, current_xy, speed)
