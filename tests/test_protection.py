import pytest
import numpy as np
import os

import ens
import ens as protection
from ens.helper import MPC


@pytest.fixture
def mpc():
    return MPC(os.path.join('cases/case33bw'))


@pytest.fixture
def nc_sw():
    return np.arange(1, 12)


@pytest.fixture
def mg_res(mpc, nc_sw):
    return ens.computation.fault_management.mgdefinition(mpc, nc_sw)


def test_mg_calc_flag_bus(mg_res):
    flag_bus = mg_res[0]
    expected_res = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 15, 15, 15, 2, 2, 2, 2, 3, 3, 3, 6, 6, 6, 6, 6,
                    6, 6, 6]
    assert len(flag_bus) == len(expected_res) and [flag_bus[i] == expected_res[i] for i in range(len(flag_bus))]


def test_mg_calc_flag_branch(mg_res):
    flag_branch = mg_res[1]
    expected_res = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 15, 15, 15, 2, 2, 2, 2, 3, 3, 3, 6, 6, 6, 6, 6, 6,
                    6, 6]
    assert len(flag_branch) == len(expected_res) and [flag_branch[i] == expected_res[i] for i in
                                                      range(len(flag_branch))]


def test_mg_calc_nc_sw_mg(mg_res):
    nc_sw_mg = mg_res[2]
    expected_res = np.array(
        [[1, 1, 2], [2, 2, 3], [3, 3, 4], [4, 4, 5], [5, 5, 6], [6, 6, 7], [7, 7, 8], [8, 8, 9], [9, 9, 10],
         [10, 10, 11], [11, 11, 12]])
    assert np.array_equal(expected_res, nc_sw_mg)



def test1_protection_type_selector(mpc):
    sw_protector = [1, 2, 3]
    faulted_branch = [15]
    livebus_loc = [15, 16]

    used_protector, lost_power_before_restoration = protection.protection_type_selector(mpc, sw_protector,
                                                                                        faulted_branch, livebus_loc)
    assert used_protector[0] == 3 and lost_power_before_restoration == 3715


def test2_protection_type_selector(mpc):
    sw_protector = [4]
    faulted_branch = [13]
    livebus_loc = [1,2,3,4]

    used_protector, lost_power_before_restoration = protection.protection_type_selector(mpc, sw_protector,
                                                                                        faulted_branch, livebus_loc)
    assert used_protector[0] == 4 and lost_power_before_restoration == 2115