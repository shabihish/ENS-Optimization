from ens.computation.protection import *
from restoration import *


def maneuvering_bus(mpc_obj, livebus_loc, livebus_auto, nc_sw_opened_loc, faulted_branch):
    if len(livebus_loc) != 0:
        livebus_temp = np.array([livebus_loc[1:]])

        mg_status1 = restoration(mpc_obj, nc_sw_opened_loc, faulted_branch, [livebus_loc[0]])

        for i in range(livebus_temp.shape[1]):

            mg_status2 = restoration(mpc_obj, nc_sw_opened_loc, faulted_branch,
                                     np.append(livebus_loc[0], livebus_temp[0, i]))
            flag_bus, flag_branch, nc_sw_mg = mgdefinition(mpc_obj, nc_sw_opened_loc)
            restored_MGs = mg_status2 - mg_status1
            restoredPower = 0
            for j in range(len(mg_status2)):
                if restored_MGs[j] == 1:
                    restoredPower += sum(
                        mpc_obj.bus.iloc[flag_bus == j + 1, 2] * mpc_obj.load_weight.iloc[flag_bus == j + 1, 0])

            if livebus_temp.shape[0] < 2:
                livebus_temp = np.append(livebus_temp, np.zeros((1, livebus_temp.shape[1])), axis=0)
            livebus_temp[1, i] = restoredPower

        livebus_temp = np.delete(livebus_temp, np.where(livebus_temp[1, :] == 0), axis=1)

        livebus_temp_sorted = np.array([[],[]])
        for i in range(len(livebus_temp[0, :])):
            x = np.argwhere(np.isin(livebus_temp[1, :], max(livebus_temp[1, :]))).T[0]
            livebus_temp_sorted = np.c_[livebus_temp_sorted, livebus_temp[:, x[0]]]
            livebus_temp = np.delete(livebus_temp, x[0], axis=1)

        # move automatic manuovering buses at first
        final_livebus_ordered = []
        livebus_auto = np.array(livebus_auto)
        for i in range(livebus_temp_sorted.shape[1] - 1, -1, -1):
            if livebus_auto[np.argwhere(np.isin(livebus_loc, livebus_temp_sorted[0, i]))] == 1:
                final_livebus_ordered.append(livebus_temp_sorted[0,i])
                livebus_temp_sorted = np.delete(livebus_temp_sorted, i, axis=1)

        if len(livebus_temp_sorted) != 0:
            final_livebus_ordered = np.append(final_livebus_ordered, livebus_temp_sorted[0, :])

        # check if manoeuvring buses do not create ring path
        unring_livebus = []
        for candidate_livebus in final_livebus_ordered:
            mg_status2 = restoration(mpc_obj, nc_sw_opened_loc, faulted_branch,
                                     np.append(livebus_loc[0],np.append(unring_livebus, candidate_livebus)))
            if sum([1 for i in range(len(mg_status1)) if mg_status1[i]!=mg_status2[i]]) > 0:
                mg_status1 = mg_status2
                unring_livebus.append(candidate_livebus)
            else:
                final_livebus_ordered = np.array(final_livebus_ordered)
                final_livebus_ordered = final_livebus_ordered[
                    np.where(np.array(final_livebus_ordered) != candidate_livebus)]
    else:
        final_livebus_ordered = []

    return final_livebus_ordered
