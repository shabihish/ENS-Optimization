import numpy as np
import restoration
from ens.computation.fault_management import mgdefinition, fault_isolation


# This function determines the recloser that breaks the current fault, neglecting the other recloser in fault isolation
def protection_type_selector(mpc_obj, sw_protector, faulted_branch, livebus_loc):
    flag_bus, flag_branch, nc_sw_mg = mgdefinition(mpc_obj, sw_protector)
    nc_sw_dis1, mg_faulted1 = fault_isolation(mpc_obj, sw_protector, faulted_branch)

    mg_faulted1, nc_sw_mg = np.array(mg_faulted1), np.array(nc_sw_mg)
    a = np.where(mg_faulted1 == 1)[1]+1

    b = np.where(nc_sw_mg[:,:, 2] == a)
    b = np.where(nc_sw_mg[:, :, 2] == np.reshape(a, (2, 1)))
    used_protector = nc_sw_mg[b[0],0]

    flag_bus, flag_branch, nc_sw_mg = mgdefinition(mpc_obj, used_protector)
    mg_status = restoration.restoration(mpc_obj, used_protector, faulted_branch, [livebus_loc[0]])

    flag_bus = [int(x) for x in flag_bus]
    lost_power_before_restoration = 0
    for i in range(len(mg_status)):
        if mg_status[i] == 0:
            additional_power_loss = mpc_obj.bus.iloc[np.where(np.array(flag_bus) == i+1)[0], 2]
            lost_power_before_restoration += np.array(additional_power_loss).sum()
    return used_protector, lost_power_before_restoration