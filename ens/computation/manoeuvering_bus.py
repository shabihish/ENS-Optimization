import numpy as np

from ens.computation.protection import *
from restoration import *


def maneuvering_bus(mpc_obj, livebus_loc, livebus_auto, nc_sw_opened_loc, faulted_branch):
    final_livebus_ordered = np.zeros((livebus_loc.shape[0], 1))
    if livebus_loc.shape[1] != 0:
        livebus_temp = np.zeros((livebus_loc.shape[0], 2, livebus_loc.shape[1] - 1), dtype=int)
        livebus_temp[:, 0, :] = livebus_loc[:, 1:]

        mg_status1 = restoration(mpc_obj, nc_sw_opened_loc, faulted_branch, livebus_loc[:, 0][..., None])

        for i in range(livebus_temp.shape[2]):

            mg_status2 = restoration(mpc_obj, nc_sw_opened_loc, faulted_branch,
                                     np.c_[livebus_loc[:, 0], livebus_temp[:, 0, i]])
            flag_bus, flag_branch, nc_sw_mg = mgdefinition(mpc_obj, nc_sw_opened_loc)
            restored_MGs = mg_status2 - mg_status1
            restoredPower = np.zeros(nc_sw_opened_loc.shape[0])

            for j in range(mg_status2.shape[1]):
                param_a = np.where(flag_bus == j + 1, mpc_obj.bus.iloc[:, 2], 0)
                param_b = np.where(flag_bus == j + 1, mpc_obj.load_weight.iloc[:, 0], 0)
                additional_restored_power = np.where(restored_MGs[:, j] == 1, np.sum(param_a * param_b, axis=1), 0)
                restoredPower += additional_restored_power

            livebus_temp[:, 1, i] = restoredPower

        # livebus_temp = np.delete(livebus_temp, np.where(livebus_temp[1, :] == 0), axis=1)
        livebus_temp = np.delete(livebus_temp[..., :, :], np.where(livebus_temp[0, 1, :] == 0), axis=2)

        livebus_temp_sorted = np.zeros(livebus_temp.shape)
        for i in range((livebus_temp[:, 0, :]).shape[1]):
            # x = livebus_temp[..., 1, :] == np.max(livebus_temp[..., 1, :], axis=1)[..., None]
            x = np.reshape(livebus_temp[..., 1, :] == (np.max(livebus_temp[..., 1, :], axis=1)[..., None]),
                           (-1, 1, livebus_temp.shape[2]))
            livebus_temp_sorted = np.c_[livebus_temp_sorted, np.where(x == True, livebus_temp[:, :, :], 0)]
            # livebus_temp = np.delete(livebus_temp, x[0], axis=1)
            livebus_temp = np.where(x == False, livebus_temp[:, :, :], 0)

        # move automatic manuovering buses first
        final_livebus_ordered = np.zeros((livebus_temp_sorted.shape[0], livebus_temp_sorted.shape[2]))
        for i in range(livebus_temp_sorted.shape[2] - 1, -1, -1):
            tmp_cond = np.where(livebus_loc == livebus_temp_sorted[:, 0, i][..., None], livebus_auto, 0).any(axis=1)
            final_livebus_ordered[:, i] = np.where(tmp_cond, livebus_temp_sorted[:, 0, i], 0)
            # livebus_temp_sorted = np.where(tmp_cond, 0, livebus_temp_sorted)
            livebus_temp_sorted[:, :, i] = np.where(tmp_cond, 0, livebus_temp_sorted[:, 0, i])[..., None]
            # livebus_temp_sorted = np.where(tmp_cond, livebus_temp_sorted[:, 0, i], 0)
            # if np.where(livebus_loc == livebus_temp_sorted[:, 0, i], livebus_auto, 0).any(axis=1) == 1:
            #     final_livebus_ordered = np.append(final_livebus_ordered, )
            #     livebus_temp_sorted = np.delete(livebus_temp_sorted, i, axis=1)

        # if livebus_temp_sorted.shape[0] != 0:
        final_livebus_ordered = np.c_[final_livebus_ordered, livebus_temp_sorted[:, 0, :]]

        # check if manoeuvring buses do not create ring path
        unring_livebus = np.zeros((final_livebus_ordered.shape[0], 1), dtype=int)[:, 0:0]
        for i in range(final_livebus_ordered.shape[1]):
            candidate_livebus = final_livebus_ordered[:, i]
            mg_status2 = restoration(mpc_obj, nc_sw_opened_loc, faulted_branch,
                                     np.ndarray.astype(np.c_[livebus_loc[:, 0], unring_livebus, candidate_livebus],
                                                       dtype=int))
            basic_cond = np.where(candidate_livebus[..., None] == 0, False, True)
            tmp_cond = (np.where(mg_status1 != mg_status2, 1, 0).sum(axis=1) > 0)[..., None]
            mg_status1 = np.where(np.logical_and(basic_cond, tmp_cond), mg_status2, mg_status1)
            unring_livebus = np.where(np.logical_and(basic_cond, tmp_cond), np.c_[unring_livebus, candidate_livebus],
                                      np.c_[unring_livebus, np.zeros((unring_livebus.shape[0], 1))])
            new_final_livebus_ordered = np.where(final_livebus_ordered != candidate_livebus[..., None],
                                                 final_livebus_ordered, 0)
            final_livebus_ordered = np.where(np.logical_and(basic_cond, np.logical_not(tmp_cond)),
                                             new_final_livebus_ordered, final_livebus_ordered)

    final_livebus_ordered = np.reshape(final_livebus_ordered,
                                       (final_livebus_ordered.shape[0], 1, final_livebus_ordered.shape[1]))
    final_livebus_ordered = np.append(final_livebus_ordered[:, :, :], np.zeros(final_livebus_ordered.shape), axis=1)
    return final_livebus_ordered
