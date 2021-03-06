import numpy as np
from ens.helper.helper import *


def calc_isolation_switch_time(mpc_obj, nc_sw_opened_loc, nc_sw_opened_auto, current_xy, speed):
    isolation_time = np.zeros(nc_sw_opened_loc.shape[0])

    new_nc_sw_opened_loc = np.zeros(nc_sw_opened_loc.shape, dtype=int)
    for i in range(nc_sw_opened_loc.shape[1] - 1, -1, -1):
        new_nc_sw_opened_loc[:, i] = np.where(nc_sw_opened_auto[:, i] != 1, nc_sw_opened_loc[:, i],
                                              new_nc_sw_opened_loc[:, i])
    nc_sw_opened_loc = new_nc_sw_opened_loc
    while nc_sw_opened_loc.any():
        dist = np.zeros(nc_sw_opened_loc.shape)
        dist_set = np.zeros(nc_sw_opened_loc.shape, dtype=bool)
        for i in range(nc_sw_opened_loc.shape[1]):
            target_xy_x = np.where(nc_sw_opened_loc[:, i]!=0, np.array(mpc_obj.branch.iloc[nc_sw_opened_loc[:, i] - 1, 0].T), 0)
            target_xy = np.array(mpc_obj.bus_xy.iloc[target_xy_x - 1, :])
            dist[:, i] = np.where(nc_sw_opened_loc[:, i] != 0, get_dist(current_xy, target_xy), np.inf)
            dist_set[:, i] = np.where(nc_sw_opened_loc[:, i] != 0, True, False)

        idx = np.argmin(dist, axis=1)

        tmp_cond = dist_set.any(axis=1)
        current_xy = np.where(tmp_cond[..., None], np.array(mpc_obj.bus_xy.iloc[
                                                            mpc_obj.branch.iloc[
                                                                nc_sw_opened_loc[np.arange(
                                                                    nc_sw_opened_loc.shape[0]), idx] - 1, 0] - 1, :]),
                              current_xy)
        new_isolation_time = isolation_time + dist[np.arange(dist.shape[0]), idx] / speed
        isolation_time = np.where(tmp_cond, new_isolation_time, isolation_time)
        # idx = idx = np.where(np.array(dist) == np.array(dist).min())[0]
        # nc_sw_opened_loc = (nc_sw_opened_loc[np.arange(nc_sw_opened_loc.shape[1]) != idx[..., None]]).reshape(
        #     nc_sw_opened_loc.shape[0], -1)


        nc_sw_opened_loc = np.where(dist == dist[np.arange(dist.shape[0]), idx][..., None], 0, nc_sw_opened_loc )


        # nc_sw_opened_loc = np.where(dist == dist[np.arange(dist.shape[0]), idx][..., None], np.inf, nc_sw_opened_loc)



    return isolation_time, current_xy
