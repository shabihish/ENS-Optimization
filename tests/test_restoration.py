import os

import numpy as np
import pytest
from ens.helper.MPC import MPC
from ens.computation.restoration import restoration


@pytest.fixture
def mpc():
    return MPC(os.path.join('data/case33bw'))

@pytest.fixture
def restoration_res1(mpc):
    nc_sw = np.array([[1, 2, 3], [1, 2, 3]])
    faulted_branch = np.array([[12, 13],[12,13]])
    livebus = np.array([[1, 1, 2, 3],[1,1,2,3]])
    return  restoration(mpc, nc_sw, faulted_branch, livebus)

@pytest.fixture
def restoration_res2(mpc):
    nc_sw = np.array([[1, 2, 3], [1, 2, 3]])
    faulted_branch = np.array([[1,15],[1,15]])
    livebus = np.array([[7,4,2,3],[7,4,2,3]])
    return  restoration(mpc, nc_sw, faulted_branch, livebus)

def test1_restoration(restoration_res1):
    exp_out = [[1,1,1,0],[1,1,1,0]]
    assert np.array_equal(restoration_res1, exp_out)

def test2_restoration(restoration_res2):
    exp_out = [[0,0,1,0],[0,0,1,0]]
    assert np.array_equal(restoration_res2, exp_out)
