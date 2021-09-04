import numpy as np
from ens.computation.calc_ENS import calc_ENS
from itertools import combinations


def optimize_ens(mpc_obj, livebus_loc, livebus_auto, sw_recloser_exist, sw_sectionalizer_exist,
                 sw_sectioner_automatic_exist, sw_sectioner_manual_exist, sw_cutout_exist, current_xy, speed,
                 num_of_new_reclosers, num_of_new_sectionalizers, num_of_new_automatic_sectioners,
                 num_of_new_manual_sectioners, num_of_new_cutouts):
    switches_arr = np.array([num_of_new_reclosers, num_of_new_cutouts,
                             num_of_new_sectionalizers, num_of_new_manual_sectioners, num_of_new_automatic_sectioners])

    # primary_ens = calc_ENS(mpc_obj, sw_recloser_exist, sw_sectionalizer_exist, sw_sectioner_automatic_exist,
    #                        sw_sectioner_manual_exist, sw_cutout_exist, livebus_loc, livebus_auto, current_xy, speed)
    # primary_ens = -1

    avail_branches = np.arange(1, mpc_obj.branch.shape[0] + 1)
    allocated_branches = np.r_[
        sw_cutout_exist, sw_recloser_exist, sw_sectionalizer_exist, sw_sectioner_automatic_exist, sw_sectioner_manual_exist]
    avail_branches = np.delete(avail_branches, allocated_branches - 1)
    return optimize( mpc_obj, avail_branches, switches_arr, sw_recloser_exist,
                                 sw_sectionalizer_exist,
                                 sw_sectioner_automatic_exist, sw_sectioner_manual_exist, sw_cutout_exist, livebus_loc,
                                 livebus_auto,
                                 current_xy, speed)


def opt_fun(branch, mpc_obj, switches_arr, sw_recloser_exist, sw_sectionalizer_exist,
            sw_sectioner_automatic_exist, sw_sectioner_manual_exist, sw_cutout_exist, livebus_loc, livebus_auto,
            current_xy, speed):
    sw_recloser_current =np.append(sw_recloser_exist, branch[:switches_arr[0]])
    sw_cutout_current =np.append(sw_cutout_exist, branch[switches_arr[0]:switches_arr[0]+switches_arr[1]])
    sw_sectionalizer_current =np.append(sw_sectionalizer_exist, branch[switches_arr[0]+switches_arr[1]:switches_arr[0]+switches_arr[1]+switches_arr[2]])
    sw_sectioner_manual_current =np.append(sw_sectioner_manual_exist, branch[switches_arr[0]+switches_arr[1]+switches_arr[2]:switches_arr[0]+switches_arr[1]+switches_arr[2]+switches_arr[3]])
    sw_sectioner_automatic_current =np.append(sw_sectioner_automatic_exist, branch[switches_arr[0]+switches_arr[1]+switches_arr[2]+switches_arr[3]:switches_arr[0]+switches_arr[1]+switches_arr[2]+switches_arr[3]+switches_arr[4]])

    # return calc_ENS(mpc_obj, sw_recloser_current, sw_sectionalizer_current,
    #         sw_sectioner_automatic_current, sw_sectioner_manual_current, sw_cutout_current, livebus_loc, livebus_auto,
    #         current_xy, speed)
    return 10
def optimize(mpc_obj, avail_branches, switches_arr, sw_recloser_exist, sw_sectionalizer_exist,
             sw_sectioner_automatic_exist, sw_sectioner_manual_exist, sw_cutout_exist, livebus_loc, livebus_auto,
             current_xy, speed):
    br_combs = np.array([x for x in combinations(avail_branches, switches_arr.sum())])
    a = np.apply_along_axis(opt_fun, axis=1, arr=br_combs, mpc_obj = mpc_obj, switches_arr=switches_arr, sw_recloser_exist=sw_recloser_exist,
                        sw_sectionalizer_exist=sw_sectionalizer_exist,
                        sw_sectioner_automatic_exist=sw_sectioner_automatic_exist,
                        sw_sectioner_manual_exist=sw_sectioner_manual_exist, sw_cutout_exist=sw_cutout_exist,
                        livebus_loc=livebus_loc, livebus_auto=livebus_auto,
