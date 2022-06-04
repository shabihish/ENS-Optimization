from ens.computation.fault_management import mgdefinition, fault_isolation
import numpy as np


def restoration(mpc_obj, nc_sw, faulted_branch, livebus):
    flag_bus, flag_branch, nc_sw_mg = mgdefinition(mpc_obj, nc_sw)
    nc_sw_dis, mg_faulted = fault_isolation(mpc_obj, nc_sw, faulted_branch)

    mg_No = np.ndarray.astype(flag_bus.max(axis=1), dtype=int)
    mg_status = np.zeros((nc_sw.shape[0], mg_No.max()))

    for i in range(livebus.shape[1]):
        x = flag_bus[np.arange(flag_bus.shape[0]), livebus[:, i] - 1] - 1
        mg_status[np.arange(mg_status.shape[0]),x] = (1 - mg_faulted[np.arange(mg_faulted.shape[0]), x])

    for i in range(mg_No.max()):
        for j in range(nc_sw.shape[1]):
            leftmg = nc_sw_mg[:, j,1] - 1
            rightmg = nc_sw_mg[:,j,2] - 1
            uu = np.maximum(mg_status[np.arange(mg_status.shape[0]), leftmg], mg_status[np.arange(mg_status.shape[0]), rightmg])
            mg_status[np.arange(mg_status.shape[0]),leftmg] = uu * (1 - mg_faulted[np.arange(mg_status.shape[0]), leftmg])
            mg_status[np.arange(mg_status.shape[0]), rightmg] = uu * (1 - mg_faulted[np.arange(mg_status.shape[0]), rightmg])

    return mg_status
