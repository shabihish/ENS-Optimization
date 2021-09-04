import numpy as np
from ens.helper.vct_helper import roll_non_zero_rows_to_beginning_sorting, roll_non_zero_rows_to_beginning_non_sorting


def mgdefinition(mpc_obj, nc_sw):
    nc_sw = np.array(nc_sw, dtype=int)
    # ******************** Defining MGs *******************
    branches = np.array(mpc_obj.branch)
    nbus = mpc_obj.bus.shape[0]
    nbranch = branches.shape[0]

    flag_bus = np.zeros((nc_sw.shape[0], nbus), dtype=int)
    flag_branch = np.zeros((nc_sw.shape[0], nbranch), dtype=int)

    nc_sw_mg = np.zeros((nc_sw.shape[0], nbus, 3), dtype=int)
    # nc_sw_mg = np.reshape(nc_sw_mg, (nc_sw.shape[0], -1))

    flag_bus[:, 0] = 1

    for i in range(nbranch):
        start_index = int(branches[i, 0]) - 1
        end_index = int(branches[i, 1]) - 1
        linked = branches[i, 10] == 1 and np.logical_not(np.isin(nc_sw, i + 1).any(axis=1))
        m = flag_bus[:, start_index]
        n = flag_bus[:, end_index]
        max_mn = np.c_[m, n].max(axis=1)
        linked_modification_cond = np.logical_or(flag_bus[:, start_index] != 0, flag_bus[:, end_index] != 0)
        linked_modification_cond = np.logical_and(linked, linked_modification_cond)

        flag_bus[:, start_index] = np.where(linked_modification_cond, max_mn, flag_bus[:, start_index])
        flag_bus[:, end_index] = np.where(linked_modification_cond, max_mn, flag_bus[:, end_index])

        flag_bus[:, start_index] = np.where(np.logical_or(linked, m) == 0,
                                            max_mn + 1,
                                            flag_bus[:, start_index])
        flag_bus[:, end_index] = np.where(np.logical_or(linked, n) == 0, max_mn + 1,
                                          flag_bus[:, end_index])

        flag_branch[:, i] = flag_bus[:, end_index]

        nc_sw_mg[:, i, 0] = np.where(linked == 0, np.ones(nc_sw.shape[0]) * (i + 1), nc_sw_mg[:, i, 0])
        nc_sw_mg[:, i, 1] = np.where(linked == 0, flag_bus[:, start_index], nc_sw_mg[:, i, 1])
        nc_sw_mg[:, i, 2] = np.where(linked == 0, flag_bus[:, end_index], nc_sw_mg[:, i, 2])

    nc_sw_mg = roll_non_zero_rows_to_beginning_sorting(nc_sw_mg, axis=1)

    return flag_bus, flag_branch, nc_sw_mg


def fault_isolation(mpc_obj, nc_sw_loc, faulted_branch):
    nc_sw_loc = roll_non_zero_rows_to_beginning_sorting(nc_sw_loc, axis=1)
    faulted_branch = np.array(faulted_branch)
    flag_bus, flag_branch, nc_sw_mg = mgdefinition(mpc_obj, nc_sw_loc)

    nc_sw_opened_loc = np.zeros((flag_bus.shape[0], nc_sw_loc.shape[1]))
    mg_No = np.ndarray.astype(flag_bus.max(axis=1), dtype=int)

    mg_faulted = np.zeros((flag_bus.shape[0], mg_No.max()))

    for i in range(faulted_branch.shape[1]):
        mgf = np.ndarray.astype(flag_branch[np.arange(flag_branch.shape[0]), faulted_branch[:, i] - 1], dtype=int)
        for j in range(nc_sw_loc.shape[1]):
            condition = np.logical_and(np.logical_or(nc_sw_mg[:, j, 1] == mgf, nc_sw_mg[:, j, 2] == mgf),
                                       np.logical_not(np.isin(nc_sw_loc[:, j], nc_sw_opened_loc)))
            nc_sw_opened_loc[:, j] = np.where(condition, nc_sw_loc[:, j], nc_sw_opened_loc[:, j])

        mg_faulted[np.arange(mgf.shape[0]), mgf - 1] = 1

    nc_sw_opened_loc = roll_non_zero_rows_to_beginning_non_sorting(nc_sw_opened_loc, axis=1)
    return nc_sw_opened_loc, mg_faulted
