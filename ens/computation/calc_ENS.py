import numpy as np

from ens.helper.helper import *
from ens.computation.protection import *
from ens.computation.calc_isolation_switch_time import calc_isolation_switch_time
from ens.computation.manoeuvering_bus import maneuvering_bus
from ens.computation.restoration import restoration
from ens.helper.vct_helper import roll_non_zero_rows_to_beginning_non_sorting
from ens.helper.vct_helper import get_next_valued_slice_along_axis, get_last_valued_slice_along_axis


def get_maneuvering_contextual_details(final_livebus_ordered, current_xy, livebus_loc, livebus_auto, bus_xy, speed):
    final_livebus_ordered = np.array(final_livebus_ordered, copy=True)
    current_xy_maneuvering_team = current_xy
    for j in range(final_livebus_ordered.shape[2]):
        tmp_cond = np.where(livebus_loc == final_livebus_ordered[:, 0, j][..., None], livebus_auto, 0).any(axis=1)
        final_livebus_ordered[:, 1, j] = np.where(tmp_cond, 0, final_livebus_ordered[:, 1, j])
        else_cond = np.logical_not(tmp_cond)

        final_livebus_ordered[:, 1, j] = np.where(
            (else_cond * (final_livebus_ordered[:, 0, j] != 0)),
            get_dist(current_xy_maneuvering_team, np.array(bus_xy.iloc[final_livebus_ordered[:, 0, j] - 1, :])) / speed,
            final_livebus_ordered[:, 1, j])

        current_xy_maneuvering_team = np.where((else_cond * (final_livebus_ordered[:, 0, j] != 0))[..., None],
                                               np.array(bus_xy.iloc[final_livebus_ordered[:, 0, j] - 1, :]),
                                               current_xy_maneuvering_team)
    maneuvering_time = final_livebus_ordered[:, 1, :].sum(axis=1)
    return current_xy_maneuvering_team, final_livebus_ordered, maneuvering_time


def calc_repair_ens(mpc_obj, ENS0, restoration_time, lost_power_before_maneuver, final_livebus_ordered, livebus_loc,
                    nc_sw_opened_loc, faulted_branch, repair_time, maneuvering_time, current_xy_maneuvering_team,
                    speed, current_xy_repair_team, nc_sw_opened_auto):
    if final_livebus_ordered.shape[2] == 0:
        return np.zeros(final_livebus_ordered.shape[0])
    ENS0 = np.array(ENS0, copy=True)
    restoration_time = np.array(restoration_time, copy=True)

    if type(repair_time) != np.ndarray:
        repair_time = np.array(repair_time)
    if type(maneuvering_time) != np.ndarray:
        maneuvering_time = np.array(maneuvering_time)

    first_nonempty_column_of_fl = get_next_valued_slice_along_axis(final_livebus_ordered, axis=2)

    ENS0 += lost_power_before_maneuver * first_nonempty_column_of_fl[:, 1]
    restoration_time += first_nonempty_column_of_fl[:, 1]

    for i in range(final_livebus_ordered.shape[2] - 1):
        livebus_new = np.ndarray.astype(np.c_[livebus_loc[:, 0][..., None], final_livebus_ordered[:, 0, :i]], dtype=int)
        flag_bus, flag_branch, nc_sw_mg = mgdefinition(mpc_obj, nc_sw_opened_loc)
        mg_status = restoration(mpc_obj, nc_sw_opened_loc, faulted_branch, livebus_new)

        lost_power1 = np.zeros(final_livebus_ordered.shape[0])

        mg_bus_indicator_sum = (np.array(mpc_obj.bus.iloc[:, 2])[..., None] * np.ndarray.astype(
            flag_bus[..., None] == np.arange(1, mg_status.shape[1] + 1), int)).sum(axis=1)
        lost_power1 += np.where((mg_status == 0) * final_livebus_ordered[:, :, i].any(axis=1)[..., None],
                                mg_bus_indicator_sum, 0).sum(axis=1)

        next_nonempty_column_of_fl = get_next_valued_slice_along_axis(final_livebus_ordered[:, :, i + 1:], axis=2)
        ENS0 += lost_power1 * next_nonempty_column_of_fl[:, 1]
        restoration_time += next_nonempty_column_of_fl[:, 1]

    livebus_new = np.ndarray.astype(np.c_[livebus_loc[:, 0][..., None], final_livebus_ordered[:, 0, :]], dtype=int)
    flag_bus, flag_branch, nc_sw_mg = mgdefinition(mpc_obj, nc_sw_opened_loc)
    mg_status = restoration(mpc_obj, nc_sw_opened_loc, faulted_branch, livebus_new)

    lost_power1 = np.zeros(final_livebus_ordered.shape[0])

    mg_bus_indicator_sum = (np.array(mpc_obj.bus.iloc[:, 2])[..., None] * np.ndarray.astype(
        flag_bus[..., None] == np.arange(1, mg_status.shape[1] + 1), int)).sum(axis=1)
    lost_power1 += np.where(mg_status == 0, mg_bus_indicator_sum, 0).sum(axis=1)

    off_time_after_restoration = repair_time - maneuvering_time
    ENS0 += lost_power1 * off_time_after_restoration

    restoration_time += repair_time
    for j in range(final_livebus_ordered.shape[2] - 1):
        final_livebus_ordered[:, 1, j] = np.where(final_livebus_ordered[:, 0, j] != 0,
                                                  get_dist(current_xy_maneuvering_team, np.array(
                                                      mpc_obj.bus_xy.iloc[final_livebus_ordered[:, 0, j] - 1,
                                                      :])) / speed,
                                                  final_livebus_ordered[:, 1, j])

        current_xy_maneuvering_team = np.where((final_livebus_ordered[:, 0, j] != 0)[..., None],
                                               np.array(mpc_obj.bus_xy.iloc[final_livebus_ordered[:, 0, j] - 1, :]),
                                               current_xy_maneuvering_team)

    for i in range(final_livebus_ordered.shape[2] - 1):
        livebus_new = np.ndarray.astype(np.c_[livebus_loc[:, 0][..., None], final_livebus_ordered[:, 0, :i - 1]],
                                        dtype=int)
        flag_bus, flag_branch, nc_sw_mg = mgdefinition(mpc_obj, nc_sw_opened_loc)
        mg_status = restoration(mpc_obj, nc_sw_opened_loc, faulted_branch, livebus_new)

        lost_power1 = np.zeros(final_livebus_ordered.shape[0])

        mg_bus_indicator_sum = (np.array(mpc_obj.bus.iloc[:, 2])[..., None] * np.ndarray.astype(
            flag_bus[..., None] == np.arange(1, mg_status.shape[1] + 1), int)).sum(axis=1)
        lost_power1 += np.where((mg_status == 0) * final_livebus_ordered[:, :, i].any(axis=1)[..., None],
                                mg_bus_indicator_sum, 0).sum(axis=1)

        next_nonempty_column_of_fl = get_next_valued_slice_along_axis(final_livebus_ordered[:, :, i + 1:], axis=2)
        ENS0 += lost_power1 * next_nonempty_column_of_fl[:, 1]
        restoration_time += next_nonempty_column_of_fl[:, 1]

    unisolation_time, current_xy_repair_team = calc_isolation_switch_time(mpc_obj, nc_sw_opened_loc,
                                                                          nc_sw_opened_auto,
                                                                          current_xy_repair_team, speed)

    livebus_new = livebus_loc[:, 0][..., None]
    flag_bus, flag_branch, nc_sw_mg = mgdefinition(mpc_obj, nc_sw_opened_loc)
    mg_status = restoration(mpc_obj, nc_sw_opened_loc, faulted_branch, livebus_new)

    lost_power1 = np.zeros(final_livebus_ordered.shape[0])

    mg_bus_indicator_sum = (np.array(mpc_obj.bus.iloc[:, 2])[..., None] * np.ndarray.astype(
        flag_bus[..., None] == np.arange(1, mg_status.shape[1] + 1), int)).sum(axis=1)
    lost_power1 += np.where(mg_status == 0,
                            mg_bus_indicator_sum, 0).sum(axis=1)

    ENS0 += lost_power1 * unisolation_time

    last_nonempty_column_of_fl = get_last_valued_slice_along_axis(final_livebus_ordered[:, :, :-1], axis=2)
    restoration_time += last_nonempty_column_of_fl[:, 1]

    added_tot_ens = ENS0 * np.array(mpc_obj.branch_reliability.iloc[faulted_branch[:, 0] - 1, 0])
    return added_tot_ens


def calc_ENS(mpc_obj, sw_recloser, sw_sectionalizer, sw_automatic_sectioner, sw_manual_sectioner, sw_cutout,
             livebus_loc, livebus_auto, current_xy, speed):
    # initialization
    sw_recloser = np.array(sw_recloser, copy=True)
    sw_sectionalizer = np.array(sw_sectionalizer, copy=True)
    sw_automatic_sectioner = np.array(sw_automatic_sectioner, copy=True)
    sw_manual_sectioner = np.array(sw_manual_sectioner, copy=True)
    sw_cutout = np.array(sw_cutout, copy=True)

    livebus_loc = np.array(livebus_loc, copy=True)
    livebus_auto = np.array(livebus_auto, copy=True)
    current_xy = np.array(current_xy, copy=True)

    mpc_obj.bus_load_factor = mpc_obj.bus_load_factor.astype(float)
    mpc_obj.bus.iloc[:, [2, 3]] = (mpc_obj.bus.iloc[:, [2, 3]] * mpc_obj.bus_load_factor.iloc[:, 0]).iloc[:, [2, 3]]

    sw_isolator_loc = np.c_[sw_automatic_sectioner, sw_manual_sectioner, sw_cutout]
    sw_isolator_auto = np.c_[np.ones(sw_automatic_sectioner.shape), np.zeros(sw_manual_sectioner.shape),
                             np.zeros(sw_cutout.shape)]
    sw_protector_loc = np.c_[sw_recloser, sw_sectionalizer]

    tot_ENS = 0

    max_h = mpc_obj.branch.shape[0]
    for h in range(1, max_h + 1):
        faulted_branch = np.ones((livebus_loc.shape[0], 1), dtype=int) * h

        temp_a = int(mpc_obj.branch.at[h - 1, 0]) - 1
        temp_b = int(mpc_obj.branch.at[h - 1, 1]) - 1
        temp_c = np.array(mpc_obj.bus_xy.iloc[temp_a, :])
        temp_d = np.array(mpc_obj.bus_xy.iloc[temp_b, :])
        fault_xy = (temp_c + temp_d) / 2
        time_to_reach_to_faulty_point = get_dist(current_xy, fault_xy) / speed
        current_xy = fault_xy

        # Choosing the recloser or sectionalizer that breaks the current fault, neglecting the other in fault isolation
        used_protector, lost_power_before_maneuver = protection_type_selector(mpc_obj, sw_protector_loc, faulted_branch,
                                                                              livebus_loc)

        # fault isolation
        nc_sw_loc = np.append(used_protector, sw_isolator_loc, axis=1)
        nc_sw_auto = np.append(np.ones((sw_isolator_auto.shape[0], 1)), sw_isolator_auto, axis=1)

        nc_sw_loc = roll_non_zero_rows_to_beginning_non_sorting(nc_sw_loc, axis=1)[:, :33]
        nc_sw_auto = roll_non_zero_rows_to_beginning_non_sorting(nc_sw_auto, axis=1)[:, :33]

        nc_sw_opened_loc, mg_faulted = fault_isolation(mpc_obj, nc_sw_loc, faulted_branch)
        nc_sw_opened_loc = nc_sw_opened_loc[:, :nc_sw_auto.shape[1]]
        nc_sw_loc = nc_sw_loc[:, :nc_sw_auto.shape[1]]

        nc_sw_opened_loc = np.where(nc_sw_opened_loc == 0, -1, nc_sw_opened_loc)
        idx_tmp = np.zeros((nc_sw_auto.shape), dtype=bool)
        for j in range(nc_sw_auto.shape[1]):
            idx_tmp = np.logical_or(idx_tmp, nc_sw_loc == nc_sw_opened_loc[:, j][np.newaxis].T)
        nc_sw_opened_loc = np.where(nc_sw_opened_loc == -1, 0, nc_sw_opened_loc)
        nc_sw_opened_auto = np.where(idx_tmp, nc_sw_auto, 0)

        # Calculating Isolation Time of Manual Switches
        isolation_time, current_xy = calc_isolation_switch_time(mpc_obj, nc_sw_opened_loc,
                                                                nc_sw_opened_auto, current_xy, speed)
        repair_time = get_dist(current_xy, fault_xy) / speed + mpc_obj.branch_reliability.iloc[
            faulted_branch[:, 0] - 1, 1]
        current_xy_repair_team = fault_xy  # Current location of the repair team

        restoration_time = mpc_obj.branch_fault_allocation_time.iloc[
                               0, faulted_branch[:, 0] - 1] + time_to_reach_to_faulty_point + isolation_time
        ENS0 = lost_power_before_maneuver * (mpc_obj.branch_fault_allocation_time.iloc[0, faulted_branch[:,
                                                                                          0] - 1] + time_to_reach_to_faulty_point + isolation_time)

        final_livebus_ordered = maneuvering_bus(mpc_obj, livebus_loc, livebus_auto, nc_sw_opened_loc, faulted_branch)
        maneuvering_time = np.zeros(nc_sw_loc.shape[0])

        # manouvering time if case
        if_cond = (final_livebus_ordered.any(axis=1).any(axis=1) == 0)
        maneuvering_time = np.where(if_cond, repair_time * 10,
                                    maneuvering_time)
        # else case
        else_cond = np.logical_not(if_cond)
        new_cxym, new_fl, new_mt = get_maneuvering_contextual_details(final_livebus_ordered, current_xy, livebus_loc,
                                                                      livebus_auto, mpc_obj.bus_xy, speed)
        current_xy_maneuvering_team = np.where(else_cond[..., None], new_cxym, current_xy)
        final_livebus_ordered[:, 1, :] = np.where(else_cond[..., None], new_fl[:, 1, :], final_livebus_ordered[:, 1, :])
        maneuvering_time = np.where(else_cond, new_mt, maneuvering_time)

        # repair ens if case
        repair_ens1 = calc_repair_ens(mpc_obj, ENS0, restoration_time, lost_power_before_maneuver,
                                      final_livebus_ordered,
                                      livebus_loc,
                                      nc_sw_opened_loc, faulted_branch, repair_time, maneuvering_time,
                                      current_xy_maneuvering_team,
                                      speed, current_xy_repair_team, nc_sw_opened_auto)

        # repair ens else case
        unisolation_time, current_xy_repair_team = calc_isolation_switch_time(mpc_obj,
                                                                              nc_sw_opened_loc,
                                                                              nc_sw_opened_auto,
                                                                              current_xy_repair_team,
                                                                              speed)
        repair_ens2 = lost_power_before_maneuver * (
                np.array(repair_time) + isolation_time + unisolation_time) * np.array(
            mpc_obj.branch_reliability.iloc[faulted_branch[:, 0] - 1, 0])

        # cases actualization
        tot_ENS += np.where(np.array(repair_time) > maneuvering_time, repair_ens1, repair_ens2)
        print('Total Progress: %{}'.format(h * 100.0 / max_h))
    return tot_ENS