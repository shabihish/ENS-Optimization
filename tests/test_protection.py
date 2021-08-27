import pytest
import numpy as np
import os

import ens
import ens as protection
from ens.helper.MPC import MPC
from ens.computation.fault_management import mgdefinition, fault_isolation


@pytest.fixture
def mpc():
    return MPC(os.path.join('cases/case33bw'))


@pytest.fixture
def nc_sw():
    return np.array([[1, 2, 3], [1, 2, 3]])


@pytest.fixture
def mg_res(mpc, nc_sw):
    return mgdefinition(mpc, nc_sw)


@pytest.fixture
def fault_isolation_res(mpc):
    return fault_isolation(mpc, [[1,2,3],[1,2,3]], 1)


# testing row 1 of mg_res
def test_mg_flag_bus1(mg_res):
    flag_bus, flag_branch, nc_sw_mg = mg_res
    assert np.array_equal(flag_bus[0, ...], np.array(
        [1., 2., 3., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 2., 2., 2., 2., 3., 3., 3., 4., 4., 4.,
         4., 4., 4., 4., 4.]))


def test_mg_flag_branch1(mg_res):
    flag_bus, flag_branch, nc_sw_mg = mg_res
    assert np.array_equal(flag_branch[0, ...],
                          np.array([2., 3., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4.,
                                    2., 2., 2., 2., 3., 3., 3., 4., 4., 4., 4., 4., 4., 4., 4.]))


def test_mg_nc_sw_mg1(mg_res):
    flag_bus, flag_branch, nc_sw_mg = mg_res
    assert np.array_equal(nc_sw_mg[0, :3, :], [[1, 1.0, 2.0], [2, 2.0, 3.0], [3, 3.0, 4.0]])


# testing row 2 of mg_res
def test_mg_flag_bus2(mg_res):
    flag_bus, flag_branch, nc_sw_mg = mg_res
    assert np.array_equal(flag_bus[1, ...], np.array(
        [1., 2., 3., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 2., 2., 2., 2., 3., 3., 3., 4., 4., 4.,
         4., 4., 4., 4., 4.]))


def test_mg_flag_branch2(mg_res):
    flag_bus, flag_branch, nc_sw_mg = mg_res
    assert np.array_equal(flag_branch[1, ...],
                          np.array([2., 3., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4., 4.,
                                    2., 2., 2., 2., 3., 3., 3., 4., 4., 4., 4., 4., 4., 4., 4.]))


def test_mg_nc_sw_mg2(mg_res):
    flag_bus, flag_branch, nc_sw_mg = mg_res
    assert np.array_equal(nc_sw_mg[1, :3, :], [[1, 1.0, 2.0], [2, 2.0, 3.0], [3, 3.0, 4.0]])


# testing row1 of fault_isolation_res
def test_fault_isolation_nc_sw_opened_loc1(fault_isolation_res):
    nc_sw_opened_loc,_ = fault_isolation_res
    assert np.array_equal(nc_sw_opened_loc[0,...]==)

@pytest.mark.skip
def test_mg_calc_flag_branch(mg_res):
    flag_branch = mg_res[1]
    expected_res = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 15, 15, 15, 2, 2, 2, 2, 3, 3, 3, 6, 6, 6, 6, 6, 6,
                    6, 6]
    assert len(flag_branch) == len(expected_res) and [flag_branch[i] == expected_res[i] for i in
                                                      range(len(flag_branch))]


@pytest.mark.skip
def test_mg_calc_nc_sw_mg(mg_res):
    nc_sw_mg = mg_res[2]
    expected_res = np.array(
        [[1, 1, 2], [2, 2, 3], [3, 3, 4], [4, 4, 5], [5, 5, 6], [6, 6, 7], [7, 7, 8], [8, 8, 9], [9, 9, 10],
         [10, 10, 11], [11, 11, 12]])
    assert np.array_equal(expected_res, nc_sw_mg)


@pytest.mark.skip
def test1_protection_type_selector(mpc):
    sw_protector = [1, 2, 3]
    faulted_branch = [15]
    livebus_loc = [15, 16]

    used_protector, lost_power_before_restoration = protection.protection_type_selector(mpc, sw_protector,
                                                                                        faulted_branch, livebus_loc)
    assert used_protector[0] == 3 and lost_power_before_restoration == 3715


@pytest.mark.skip
def test2_protection_type_selector(mpc):
    sw_protector = [4]
    faulted_branch = [13]
    livebus_loc = [1, 2, 3, 4]

    used_protector, lost_power_before_restoration = protection.protection_type_selector(mpc, sw_protector,
                                                                                        faulted_branch, livebus_loc)
    assert used_protector[0] == 4 and lost_power_before_restoration == 2115
