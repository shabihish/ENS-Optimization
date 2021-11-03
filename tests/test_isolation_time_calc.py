import os

import numpy as np
import pytest
from ens.helper.MPC import MPC
from ens.computation.calc_isolation_switch_time import calc_isolation_switch_time


@pytest.fixture
def mpc():
    return MPC(os.path.join('data/case33bw'))


# @pytest.mark.skip
def test1_isolation_time_calc(mpc):
    nc_sw_opened_loc, nc_sw_opened_auto, current_xy, speed = np.array([[1, 2, 6], [1, 2, 6]]), np.array(
        [[1, 4, 5], [1, 4, 5]]), np.array([1, 2]), 10

    isolation_time, current_xy = calc_isolation_switch_time(mpc, nc_sw_opened_loc, nc_sw_opened_auto, current_xy, speed)
    assert np.array_equal(np.round(isolation_time, 3), [1.024, 1.024]) and np.array_equal(np.array(current_xy),
                                                                                          np.array([[-8, 0], [-8, 0]]))


# @pytest.mark.skip
def test2_isolation_time_calc(mpc):
    nc_sw_opened_loc, nc_sw_opened_auto, current_xy, speed = np.array([[20, 21, 22], [20, 21, 22]]), np.array(
        [[2, 4, 8], [2, 4, 8]]), np.array([
        [1, 7], [1, 7]]), 16

    isolation_time, current_xy = calc_isolation_switch_time(mpc, nc_sw_opened_loc, nc_sw_opened_auto, current_xy, speed)
    assert np.array_equal(np.round(isolation_time, 3), [0.684, 0.684]) and np.array_equal(np.array(current_xy),
                                                                                          np.array([[-6, 0], [-6, 0]]))


def test3_isolation_time_calc(mpc):
    nc_sw_opened_loc, nc_sw_opened_auto, current_xy, speed = np.array([[5, 6, 0], [5, 6, 0]]), np.array(
        [[0, 0, 0], [0, 0, 0]]), np.array([
        [-1, 0], [-1, 0]]), 50

    isolation_time, current_xy = calc_isolation_switch_time(mpc, nc_sw_opened_loc, nc_sw_opened_auto, current_xy, speed)
    assert np.array_equal(isolation_time, [0.02, 0.02]) and np.array_equal(np.array(current_xy),
                                                                                          np.array([[-2, 0], [-2, 0]]))
