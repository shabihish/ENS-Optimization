import numpy as np
import copy as cp
from Switch import Switch
from ens.computation.calc_ENS import calc_ENS


def optimize_ens(mpc_obj, livebus_loc, livebus_auto, sw_recloser_exist, sw_sectionalizer_exist,
                 sw_sectioner_automatic_exist, sw_sectioner_manual_exist, sw_cutout_exist, current_xy, speed,
                 num_of_new_reclosers, num_of_new_sectionalizers, num_of_new_automatic_sectioners,
                 num_of_new_manual_sectioners, num_of_new_cutouts):
    switches_arr = np.array([num_of_new_reclosers, num_of_new_cutouts,
                             num_of_new_sectionalizers, num_of_new_manual_sectioners, num_of_new_automatic_sectioners])

    primary_ens = calc_ENS(mpc_obj, sw_recloser_exist, sw_sectionalizer_exist, sw_sectioner_automatic_exist,
                           sw_sectioner_manual_exist, sw_cutout_exist, livebus_loc, livebus_auto, current_xy, speed)
    # primary_ens = -1

    avail_branches = np.arange(1, mpc_obj.branch.shape[0] + 1)
    allocated_branches = np.r_[
        sw_cutout_exist, sw_recloser_exist, sw_sectionalizer_exist, sw_sectioner_automatic_exist, sw_sectioner_manual_exist]
    avail_branches = np.delete(avail_branches, allocated_branches - 1)
    return primary_ens, optimize(primary_ens, mpc_obj, avail_branches, switches_arr, sw_recloser_exist,
                                 sw_sectionalizer_exist,
                                 sw_sectioner_automatic_exist, sw_sectioner_manual_exist, sw_cutout_exist, livebus_loc,
                                 livebus_auto,
                                 current_xy, speed)


def optimize(current_ens, mpc_obj, avail_branches, switches_arr, sw_recloser_exist, sw_sectionalizer_exist,
             sw_sectioner_automatic_exist, sw_sectioner_manual_exist, sw_cutout_exist, livebus_loc, livebus_auto,
             current_xy, speed):
    switches_loc_bin = np.where(switches_arr >= 1)[0]
    for i in range(switches_loc_bin.shape[0]):
        sw_recloser_current = []
        sw_cutout_current = []
        sw_sectionalizer_current = []
        sw_sectioner_manual_current = []
        sw_sectioner_automatic_current = []

        sw = switches_loc_bin[i]
        for br_idx in range(avail_branches.shape[0]):
            branch = avail_branches[br_idx]
            if sw == Switch.SW_RECLOSER:
                sw_recloser_current = [branch]
            elif sw == Switch.SW_CUTOUT:
                sw_cutout_current = [branch]
            elif sw == Switch.SW_SECTIONALIZER:
                sw_sectionalizer_current = [branch]
            elif sw == Switch.SW_MSECTIONER:
                sw_sectioner_manual_current = [branch]
            elif sw == Switch.SW_ASECTIONER:
                sw_sectioner_automatic_current = [branch]

            new_switches_arr = np.array(switches_arr, copy=True)
            new_switches_arr[sw] -= 1

            current_ens = min(optimize(current_ens, mpc_obj, np.delete(avail_branches, br_idx), new_switches_arr,
                                       np.append(sw_recloser_exist, sw_recloser_current),
                                       np.append(sw_sectionalizer_exist, sw_sectionalizer_current),
                                       np.append(sw_sectioner_automatic_exist, sw_sectioner_automatic_current),
                                       np.append(sw_sectioner_manual_exist, sw_sectioner_manual_current),
                                       np.append(sw_cutout_exist, sw_cutout_current),
                                       livebus_loc,
                                       livebus_auto, current_xy, speed), current_ens)
            # switches_arr[sw] += 1
        switches_loc_bin = np.where(switches_arr >= 1)[0]

    # return min(current_ens, calc_ENS(mpc_obj, sw_recloser_exist, sw_sectionalizer_exist, sw_sectioner_automatic_exist,
    #                                  sw_sectioner_manual_exist, sw_cutout_exist, livebus_loc, livebus_auto, current_xy,
    #                                  speed))
    return min(current_ens, current_ens - 1)

    np.array([x for x in combinations(np.arange(1, 32), 6)])
