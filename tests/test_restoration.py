import os

import numpy as np
import pytest
from ens.helper import MPC
from ens.computation.restoration import restoration


@pytest.fixture
def mpc():
    return MPC(os.path.join('cases/case33bw'))


def test1_restoration(mpc):
    nc_sw = [1, 2, 3]
    faulted_branch = [12, 13]
    livebus = [1, 1, 2, 3]
    rest_out = restoration(mpc, nc_sw, faulted_branch, livebus)
    exp_out = [1,1,1,0]
    assert np.array_equal(rest_out, exp_out)

def test2_restoration(mpc):
    nc_sw = [1, 2, 3]
    faulted_branch = [1,15]
    livebus = [7, 4, 2, 3]
    rest_out = restoration(mpc, nc_sw, faulted_branch, livebus)
    exp_out = [0,0,1,0]
    assert np.array_equal(rest_out, exp_out)
