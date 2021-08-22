from ens.helper.helper import *
from ens.computation.protection import *
from ens.computation.calc_isolation_switch_time import calc_isolation_switch_time
from ens.computation.manoeuvering_bus import maneuvering_bus
from ens.computation.restoration import restoration


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

    sw_isolator_loc = np.r_[sw_automatic_sectioner, sw_manual_sectioner, sw_cutout]
    sw_isolator_auto = np.r_[np.ones(sw_automatic_sectioner.shape), np.zeros(sw_manual_sectioner.shape),
                             np.zeros(sw_cutout.shape)]
    sw_protector_loc = np.append(sw_recloser, sw_sectionalizer)

    tot_ENS = 0
    for h in range(1, mpc_obj.branch.shape[0] + 1):
        faulted_branch = [h]

        temp_a = int(mpc_obj.branch.at[faulted_branch[0] - 1, 0]) - 1
        temp_b = int(mpc_obj.branch.at[faulted_branch[0] - 1, 1]) - 1
        temp_c = mpc_obj.bus_xy.iloc[temp_a, :]
        temp_d = mpc_obj.bus_xy.iloc[temp_b, :]
        fault_xy = (temp_c + temp_d) / 2
        time_to_reach_to_faulty_point = get_dist(current_xy, fault_xy) / speed
        current_xy = fault_xy

        # Choosing the recloser or sectionalizer that breaks the current fault and neglecting the other in fault isolation
        used_protector, lost_power_before_maneuver = protection_type_selector(mpc_obj, sw_protector_loc, faulted_branch,
                                                                              livebus_loc)

        # fault isolation
        nc_sw_loc = np.append(used_protector, sw_isolator_loc)
        nc_sw_auto = np.append([1], sw_isolator_auto)

        nc_sw_opened_loc, mg_faulted = fault_isolation(mpc_obj, nc_sw_loc, faulted_branch)
        _, index_of_nc_sw_opened_loc_in_nc_sw_loc = is_member(nc_sw_opened_loc, nc_sw_loc)
        nc_sw_opened_auto = nc_sw_auto[index_of_nc_sw_opened_loc_in_nc_sw_loc]

        # Calculating Isolation Time of Manual Switches
        isolation_time, current_xy = calc_isolation_switch_time(mpc_obj, nc_sw_opened_loc,
                                                                nc_sw_opened_auto, current_xy, speed)
        repair_time = get_dist(current_xy, fault_xy) / speed + mpc_obj.branch_reliability.at[faulted_branch[0] - 1, 1]
        current_xy_repair_team = fault_xy  # Current location of the repair team

        restoration_time = mpc_obj.branch_fault_allocation_time.at[0,
                                                                   faulted_branch[
                                                                       0] - 1] + time_to_reach_to_faulty_point + isolation_time
        ENS0 = lost_power_before_maneuver * (
                mpc_obj.branch_fault_allocation_time.at[0,
                                                        faulted_branch[
                                                            0] - 1] + time_to_reach_to_faulty_point + isolation_time)

        final_livebus_ordered = maneuvering_bus(mpc_obj, livebus_loc, livebus_auto, nc_sw_opened_loc, faulted_branch)

        maneuvering_time = 0
        current_xy_maneuvering_team = current_xy
        if final_livebus_ordered.shape[1] == 0:
            maneuvering_time = repair_time * 10
        else:
            current_xy_maneuvering_team = current_xy  # current loc of manuovering team

            for i in range(final_livebus_ordered.shape[1]):
                if livebus_auto[np.where(livebus_loc == final_livebus_ordered[i])] == 1:
                    final_livebus_ordered[1, i] = 0
                else:
                    final_livebus_ordered[1, i] = get_dist(current_xy_maneuvering_team,
                                                           mpc_obj.bus_xy.iloc[int(final_livebus_ordered[0, i]) - 1,
                                                           :]) / speed
                    current_xy_maneuvering_team = mpc_obj.bus_xy.iloc[int(final_livebus_ordered[1, i]) - 1, :]

            maneuvering_time = final_livebus_ordered[1, :].sum()

        if repair_time > maneuvering_time:
            # Ens Calculation During Manuovering
            ENS0 += lost_power_before_maneuver * final_livebus_ordered[1, 0]
            restoration_time += final_livebus_ordered[1, 0]

            for i in range(final_livebus_ordered[0, :].shape[0] - 1):
                livebus_new = np.r_[livebus_loc[0], final_livebus_ordered[0, 0:i]]
                flag_bus, flag_branch, nc_sw_mg = mgdefinition(mpc_obj, nc_sw_opened_loc)
                mg_status = restoration(mpc_obj, nc_sw_opened_loc, faulted_branch, livebus_new)
                lost_power1 = 0

                for j in range(mg_status.shape[0]):
                    if mg_status[j] == 0:
                        lost_power1 += sum(mpc_obj.bus.iloc[flag_bus == j + 1, 2])

                ENS0 += lost_power1 * final_livebus_ordered[1, i + 1]
                restoration_time = restoration_time + final_livebus_ordered[1, i + 1]

            livebus_new = np.r_[livebus_loc[0], final_livebus_ordered[0, :]]
            flag_bus, flag_branch, nc_sw_mg = mgdefinition(mpc_obj, nc_sw_opened_loc)
            mg_status = restoration(mpc_obj, nc_sw_opened_loc, faulted_branch, livebus_new)
            lost_power1 = 0
            for j in range(mg_status.shape[0]):
                if mg_status[j] == 0:
                    lost_power1 += sum(mpc_obj.bus.iloc[flag_bus == j + 1, 2])

            OffTimeAfterRestoration = repair_time - maneuvering_time
            ENS0 += lost_power1 * OffTimeAfterRestoration
            # TODO: verify the timing
            restoration_time += repair_time

            # Disconnecting maneuver points
            for i in range(final_livebus_ordered[0, :].shape[0] - 1, -1, -1):
                if final_livebus_ordered[1, i] != 0:
                    final_livebus_ordered[1, i] = get_dist(current_xy_maneuvering_team, mpc_obj.bus_xy
                                                           .iloc[int(final_livebus_ordered[0, i]) - 1, :]) / speed
                    current_xy_maneuvering_team = mpc_obj.bus_xy.iloc[int(final_livebus_ordered[1, i]) - 1, :]

            for i in range(final_livebus_ordered[1, :].shape[0] - 1, -1 - 1):
                livebus_new = np.c_[livebus_loc[0], final_livebus_ordered[0, 0:i - 1]]
                flag_bus, flag_branch, nc_sw_mg = mgdefinition(mpc_obj, nc_sw_opened_loc)
                mg_status = restoration(mpc_obj, nc_sw_opened_loc, faulted_branch[0], livebus_new)
                lost_power1 = 0
                for j in range(mg_status):
                    if mg_status[j] == 0:
                        lost_power1 += sum(mpc_obj.bus.iloc[flag_bus == j + 1, 2])

                ENS0 += lost_power1 * final_livebus_ordered[1, i - 1]
                restoration_time = restoration_time + final_livebus_ordered[1, i - 1]

            # ENS calculation afer removing fault
            UnIsolation_time, current_xy_repair_team = calc_isolation_switch_time(mpc_obj, nc_sw_opened_loc,
                                                                                  nc_sw_opened_auto,
                                                                                  current_xy_repair_team, speed)
            livebus_new = [livebus_loc[0]]
            flag_bus, flag_branch, nc_sw_mg = mgdefinition(mpc_obj, nc_sw_opened_loc)
            mg_status = restoration(mpc_obj, nc_sw_opened_loc, faulted_branch, livebus_new)
            lost_power1 = 0

            for j in range(mg_status.shape[0]):
                if mg_status[j] == 0:
                    lost_power1 += sum(mpc_obj.bus.iloc[flag_bus == j + 1, 2])

            ENS0 += lost_power1 * UnIsolation_time
            restoration_time += final_livebus_ordered[1, i - 1]

            tot_ENS += ENS0 * mpc_obj.branch_reliability.at[faulted_branch[0] - 1, 0]
        else:
            UnIsolation_time, current_xy_repair_team = calc_isolation_switch_time(mpc_obj,
                                                                                  nc_sw_opened_loc,
                                                                                  nc_sw_opened_auto,
                                                                                  current_xy_repair_team,
                                                                                  speed)
            tot_ENS += lost_power_before_maneuver * (
                    repair_time + isolation_time + UnIsolation_time) * mpc_obj.branch_reliability.at[
                           faulted_branch[0] - 1, 0]

    return tot_ENS
