from ens.helper import MPC
from ens.computation.calc_ENS import *
import os, pytest

@pytest.fixture
def mpc():
    return MPC(os.path.join('cases/case33bw'))

def test_calc_ENS(mpc):
    livebus_loc = [1, 18, 22, 25, 33]
    livebus_auto = [1, 1, 0, 0, 0]
    sw_recloser = [1, 7]  # %branch number of Reclousers
    sw_sectionalizer = []  # #    %branch number of Sectionalizers
    sw_automatic_sectioner = []  # %branch number and Automatic
    sw_manual_sectioner = [6, 5]
    sw_cutout = []  # %Location and Automatic (1)/Manual (0) disconnector switches
    current_xy = [-10, -10]  # %The current location of maintenance group
    speed = 50

    tot_ENS = calc_ENS(mpc, sw_recloser, sw_sectionalizer, sw_automatic_sectioner, sw_manual_sectioner, sw_cutout,
                         livebus_loc, livebus_auto, current_xy, speed)
