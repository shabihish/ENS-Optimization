import os
import pytest
from ens.helper.MPC import MPC
from ens.computation.manoeuvering_bus import maneuvering_bus
import numpy as np


@pytest.fixture
def mpc():
    return MPC(os.path.join('cases/case33bw'))


def test1_maneuvering_bus(mpc):
    livebus_loc = np.array([[1, 18, 22, 25, 33], [1, 18, 22, 25, 33]])
    livebus_auto = np.array([[1, 0, 0, 0, 1], [1, 0, 0, 0, 1]])
    nc_sw_opened_loc = np.array([[1, 5], [1, 5]])
    faulted_branch = np.array([[1], [1]])

    res = maneuvering_bus(mpc, livebus_loc, livebus_auto, nc_sw_opened_loc, faulted_branch)
    assert res == 33


def test2_maneuvering_bus(mpc):
    livebus_loc = [1, 11, 21, 25]
    livebus_auto = [1, 0, 1, 1]
    nc_sw_opened_loc = [11, 7]
    faulted_branch = [21]

    res = maneuvering_bus(mpc, livebus_loc, livebus_auto, nc_sw_opened_loc, faulted_branch)
    assert res == 11
