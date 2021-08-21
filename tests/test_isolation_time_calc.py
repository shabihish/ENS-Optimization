import os

import numpy as np
import pytest
from ens.helper import MPC
from ens.computation.calc_isolation_switch_time import calc_isolation_switch_time


@pytest.fixture
def mpc():
    return MPC(os.path.join('cases/case33bw'))


def test1_isolation_time_calc(mpc):
    nc_sw_opened_loc, nc_sw_opened_auto, current_xy, speed = [1, 2, 6], [1, 4, 5], [1, 2], 10

    isolation_time, current_xy = calc_isolation_switch_time(mpc, nc_sw_opened_loc, nc_sw_opened_auto, current_xy, speed)
    assert round(isolation_time, 3) == 1.024 and np.array_equal(np.array(current_xy), np.array([-8, 0]))

def test2_isolation_time_calc(mpc):
    nc_sw_opened_loc, nc_sw_opened_auto, current_xy, speed = [20,21,22], [2,4,8], [1,7], 16

    isolation_time, current_xy = calc_isolation_switch_time(mpc, nc_sw_opened_loc, nc_sw_opened_auto, current_xy, speed)
    assert round(isolation_time, 3) == 0.684 and np.array_equal(np.array(current_xy), np.array([-6, 0]))
