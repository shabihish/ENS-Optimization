import numpy as np
from ens.computation.restoration import restoration
from ens.computation.fault_management import mgdefinition, fault_isolation
from ens.helper.vct_helper import roll_non_zero_rows_to_beginning_sorting


# This function determines the recloser that breaks the current fault, neglecting the other recloser in fault isolation
def protection_type_selector(mpc_obj, sw_protector, faulted_branch, livebus_loc):
    flag_bus, flag_branch, nc_sw_mg = mgdefinition(mpc_obj, sw_protector)
    nc_sw_dis1, mg_faulted1 = fault_isolation(mpc_obj, sw_protector, faulted_branch)

    mg_faulted1, nc_sw_mg = np.array(mg_faulted1), np.array(nc_sw_mg)
    a = np.where(mg_faulted1 == 1)[1] + 1

    b_arr = nc_sw_mg[:, :, 2] == a[np.newaxis].T
    # b = np.count_nonznp.array(ero(b_arr, axis=1)
    # b = np.zeros((nc_sw_mg.shape[0], b.max()))
    # b = np.where(nc_sw_mg[:, :, 2] == np.reshape(a, (2, 1)))

    used_protector = np.zeros((nc_sw_mg.shape[0], nc_sw_mg.shape[1]))
    used_protector = np.where(b_arr, nc_sw_mg[:, :, 0], 0)
    used_protector = roll_non_zero_rows_to_beginning_sorting(used_protector, axis=1)
    # used_protector = nc_sw_mg[b[0], 0]

    flag_bus, flag_branch, nc_sw_mg = mgdefinition(mpc_obj, used_protector)
    mg_status = restoration(mpc_obj, used_protector, faulted_branch, livebus_loc)

    lost_power_before_restoration = np.zeros(mg_status.shape[0])
    for i in range(mg_status.shape[1]):
        additional_power_loss = np.where(flag_bus == i + 1, mpc_obj.bus.iloc[:, 2], 0)
        lost_power_before_restoration = np.where(mg_status[:, i] == 0,
                                                 lost_power_before_restoration + additional_power_loss.sum(axis=1),
                                                 lost_power_before_restoration)

        # if mg_status[:, i] == 0:
        #     additional_power_loss = mpc_obj.bus.iloc[np.where(flag_bus == i + 1)[0], 2]
        #     lost_power_before_restoration += np.array(additional_power_loss).sum()
    return used_protector, lost_power_before_restoration
