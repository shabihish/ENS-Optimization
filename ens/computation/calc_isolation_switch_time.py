import numpy as np

from ens.helper.helper import *


def calc_isolation_switch_time(mpc_obj, nc_sw_opened_loc, nc_sw_opened_auto, current_xy, speed):
    isolation_time = 0

    new_nc_sw_opened_loc = []
    for i in range(len(nc_sw_opened_loc) - 1, -1, -1):
        if nc_sw_opened_auto[i] != 1:
            new_nc_sw_opened_loc.append(nc_sw_opened_loc[i])
    nc_sw_opened_loc = new_nc_sw_opened_loc
    nc_sw_opened_loc.reverse()
    nc_sw_opened_loc = np.array(nc_sw_opened_loc)

    while len(nc_sw_opened_loc) != 0:
        dist = []
        for i in range(len(nc_sw_opened_loc)):
            target_xy_x = mpc_obj.branch.iloc[int(nc_sw_opened_loc[i])-1, 0]
            target_xy = mpc_obj.bus_xy.iloc[int(target_xy_x)-1, :]
            dist.append(get_dist(current_xy, [target_xy[0],target_xy[1]]))

        idx = np.where(np.array(dist) == np.array(dist).min())[0]
        current_xy = mpc_obj.bus_xy.iloc[int(mpc_obj.branch.iloc[int(nc_sw_opened_loc[int(idx[0])])-1, 0])-1, :]
        isolation_time += dist[idx[0]] / speed
        nc_sw_opened_loc = np.delete(nc_sw_opened_loc, idx)

    return isolation_time, current_xy
