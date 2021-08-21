import numpy as np
import copy


def mgdefinition(mpc_obj, nc_sw):
    nc_sw = np.array([int(x) for x in nc_sw])
    nc_sw.sort()
    # ******************** Defining MGs *******************
    mpc_obj =copy.deepcopy(mpc_obj)
    mpc_obj.branch.iloc[nc_sw - 1, 10] = 0
    nbus = mpc_obj.bus.shape[0]
    nbranch = mpc_obj.branch.shape[0]

    flag_bus = np.zeros(nbus)
    flag_branch = np.zeros(nbranch)

    nc_sw_mg = []

    flag_bus[0] = 1
    brbus = mpc_obj.branch.iloc[0:nbranch, [0, 1, 10]]

    for i in range(nbranch):
        start_index = int(brbus.iloc[i, 0]) - 1
        end_index = int(brbus.iloc[i, 1]) - 1
        linked = int(brbus.iloc[i, 2])

        if linked == 1:
            if flag_bus[start_index] != 0 or flag_bus[end_index] != 0:
                m = flag_bus[start_index]
                n = flag_bus[end_index]

                max_mn = max(n, m)
                flag_bus[start_index] = max_mn
                flag_bus[end_index] = max_mn
            flag_branch[i] = flag_bus[end_index]

        else:
            m = flag_bus[start_index]
            n = flag_bus[end_index]
            if n == 0:
                flag_bus[end_index] = flag_bus.max() + 1
            elif m == 0:
                flag_bus[start_index] = flag_bus.max() + 1

            flag_branch[i] = flag_bus[end_index]

            nc_sw_mg.append([i + 1, flag_bus[start_index], flag_bus[end_index]])
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