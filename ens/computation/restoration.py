from ens.computation.fault_management import mgdefinition, fault_isolation
import numpy as np

def restoration(mpc_obj, nc_sw, faulted_branch, livebus):
    flag_bus, flag_branch, nc_sw_mg = mgdefinition(mpc_obj, nc_sw)
    nc_sw_dis, mg_faulted = fault_isolation(mpc_obj, nc_sw, faulted_branch)

    mg_No = int(flag_bus.max())
    mg_status = np.zeros(mg_No)

    for i in range(len(livebus)):
        x = int(flag_bus[int(livebus[i])-1])-1
        mg_status[x] = (1 - mg_faulted[x])

    for i in range(mg_No):
        for j in range(len(nc_sw)):
            leftmg = int(nc_sw_mg[j][1]) - 1
            rightmg = int(nc_sw_mg[j][2]) - 1
            uu = max(mg_status[leftmg], mg_status[rightmg])
            mg_status[leftmg] = uu * (1 - mg_faulted[leftmg])
            mg_status[rightmg] = uu * (1 - mg_faulted[rightmg])

    return mg_status
