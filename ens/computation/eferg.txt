import numpy as np


def mgdefinition(mpc_obj, nc_sw):
    nc_sw = np.array(nc_sw, dtype=int)
    # ******************** Defining MGs *******************
    branches = np.array(mpc_obj.branch)
    nbus = mpc_obj.bus.shape[0]
    nbranch = branches.shape[0]

    flag_bus = np.zeros((nc_sw.shape[0], nbus))
    flag_branch = np.zeros((nc_sw.shape[0], nbranch))

    nc_sw_mg = np.zeros((nc_sw.shape[0], nbus, 3))
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

        flag_branch[:, i] = np.where(linked, flag_bus[:, end_index],
                                     flag_branch[:, i])

        nc_sw_mg[:, i, 0] = np.where(linked == 0, np.ones(nc_sw.shape[0]) * i, nc_sw_mg[:, i, 0])
        nc_sw_mg[:, i, 1] = np.where(linked == 0, flag_bus[:, start_index], nc_sw_mg[:, i, 1])
        nc_sw_mg[:, i, 2] = np.where(linked == 0, flag_bus[:, end_index], nc_sw_mg[:, i, 2])

        # nc_sw_mg.append([i + 1, flag_bus[start_index], flag_bus[end_index]])
        # if linked == 1:
        #     if flag_bus[start_index] != 0 or flag_bus[end_index] != 0:
        #         m = flag_bus[start_index]
        #         n = flag_bus[end_index]
        #
        #         max_mn = max(n, m)
        #         flag_bus[start_index] = max_mn
        #         flag_bus[end_index] = max_mn
        #     flag_branch[i] = flag_bus[end_index]
        #
        # else:
        #     m = flag_bus[start_index]
        #     n = flag_bus[end_index]
        #     if n == 0:
        #         flag_bus[end_index] = flag_bus.max() + 1
        #     elif m == 0:
        #         flag_bus[start_index] = flag_bus.max() + 1
        #
        #     flag_branch[i] = flag_bus[end_index]
        #
        #     nc_sw_mg.append([i + 1, flag_bus[start_index], flag_bus[end_index]])
    return flag_bus, flag_branch, nc_sw_mg


def fault_isolation(mpc_obj, nc_sw_loc, faulted_branch):
    nc_sw_loc = np.array(nc_sw_loc)
    nc_sw_loc.sort()
    faulted_branch = np.array(faulted_branch)
    flag_bus, flag_branch, nc_sw_mg = mgdefinition(mpc_obj, nc_sw_loc)

    nc_sw_opened_loc = []
    mg_No = int(flag_bus.max())

    mg_faulted = np.zeros(mg_No)

    for i in range(len(faulted_branch)):
        mgf = flag_branch[faulted_branch[i] - 1]
        for j in range(len(nc_sw_loc)):
            if nc_sw_mg[j][1] == mgf or nc_sw_mg[j][2] == mgf:
                if int(nc_sw_loc[j]) not in nc_sw_opened_loc:
                    nc_sw_opened_loc.append(nc_sw_loc[j])

        mg_faulted[int(mgf) - 1] = 1
    return nc_sw_opened_loc, mg_faulted
