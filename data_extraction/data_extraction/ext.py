import os

import numpy as np
import sys
from netgraph import *
from helper import *


def get_ordinary_net_graph(segments_start_x, segments_end_x, segments_start_y, segments_end_y,
                           points_set_rounding_ndigits):
    temp_len = segments_end_y.shape[0]
    if temp_len <= 0 or temp_len != segments_start_y.shape[0] or temp_len != segments_start_x.shape[
        0] or temp_len != \
            segments_end_x.shape[0]:
        raise Exception("Invalid input segments given for graph construction.")

    net_graph = NetGraph()
    points = {}
    points_approx = {}
    for i in range(temp_len):
        p1_key = str(segments_start_x[i]) + ',' + str(segments_start_y[i])
        p2_key = str(segments_end_x[i]) + ',' + str(segments_end_y[i])
        if p1_key not in points:
            p1 = Point(segments_start_x[i], segments_start_y[i], 0)
            points[p1_key] = p1

            approx_key = str(round(p1.x, points_set_rounding_ndigits)) + ',' + str(
                round(p1.y, points_set_rounding_ndigits))
            points_approx[approx_key] = p1
        else:
            p1 = points[p1_key]

        if p2_key not in points:
            p2 = Point(segments_end_x[i], segments_end_y[i], 0)
            points[p2_key] = p2

            approx_key = str(round(p2.x, points_set_rounding_ndigits)) + ',' + str(
                round(p2.y, points_set_rounding_ndigits))
            points_approx[approx_key] = p2
        else:
            p2 = points[p2_key]

        net_graph.add_edge(p1, p2)
    return net_graph, points, points_approx


get_dist = lambda x1, x2, y1, y2: ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


def get_closest_point(p_x, p_y, key_func, points_approx, points_set_rounding_ndigits, radius=2, step_size=1):
    min_dist = radius + 1
    closest_point_key = None
    for x in np.arange(int(p_x) - radius, int(p_x) + radius + 1, step_size):
        for y in np.arange(int(p_y) - radius, int(p_y) + radius + 1, step_size):
            key = key_func(x, y, points_set_rounding_ndigits)
            if key in points_approx:
                dist = get_dist(p_x, x, p_y, y)
                if dist < min_dist:
                    min_dist = dist
                    closest_point_key = key
    return closest_point_key, min_dist


def get_closest_point_dynamically(x, y, key_func, points_approx, min_dist_radius, max_dist_radius,
                                  points_set_rounding_ndigits, step_size=1):
    closest_point = None
    min_dist = max_dist_radius + 1
    for radius in np.arange(min_dist_radius, max_dist_radius + 1, step_size):
        closest_point, min_dist = get_closest_point(x, y, key_func, points_approx,
                                                    points_set_rounding_ndigits, radius, step_size)
        if closest_point is not None:
            break

    return closest_point, min_dist


def add_JMPRs_to_net_graph(net_graph, points, points_approx, JMPR_start_x, JMPR_end_x, JMPR_start_y, JMPR_end_y,
                           min_dist_radius,
                           max_dist_radius, points_set_rounding_ndigits):
    temp_len = JMPR_end_y.shape[0]
    if temp_len <= 0 or temp_len != JMPR_start_y.shape[0] or temp_len != JMPR_start_x.shape[
        0] or temp_len != \
            JMPR_end_x.shape[0]:
        raise Exception("Invalid input segments given for graph JMPRs.")

    key_func = lambda p_x, p_y, points_set_rounding_ndigits: str(round(p_x, points_set_rounding_ndigits)) + ',' + str(
        round(p_y, points_set_rounding_ndigits))

    for i in range(temp_len):
        p1_key, r1 = get_closest_point_dynamically(JMPR_start_x[i], JMPR_start_y[i], key_func, points_approx,
                                                   min_dist_radius,
                                                   max_dist_radius, points_set_rounding_ndigits,
                                                   step_size=0.1 ** points_set_rounding_ndigits)
        p2_key, r2 = get_closest_point_dynamically(JMPR_end_x[i], JMPR_end_y[i], key_func, points_approx,
                                                   min_dist_radius,
                                                   max_dist_radius, points_set_rounding_ndigits,
                                                   step_size=0.1 ** points_set_rounding_ndigits)
        if p1_key == p2_key:
            if r1 <= r2:
                p2_key = None
            else:
                p1_key = None

        if p1_key is not None:
            p1 = points_approx[p1_key]
        else:
            key = str(JMPR_start_x[i]) + ',' + str(JMPR_start_y[i])
            if key not in points:
                p1 = Point(JMPR_start_x[i], JMPR_start_y[i], 0)
                points[key] = p1
                points_approx[key_func(JMPR_start_x[i], JMPR_start_y[i], points_set_rounding_ndigits)] = p1
            else:
                raise Exception('Search has not been successful in JMPR point placement.')

        if p2_key is not None:
            p2 = points_approx[p2_key]
        else:
            key = str(JMPR_end_x[i]) + ',' + str(JMPR_end_y[i])
            if key not in points:
                p2 = Point(JMPR_end_x[i], JMPR_end_y[i], 0)
                points[key] = p2
                points_approx[key_func(JMPR_end_x[i], JMPR_end_y[i], points_set_rounding_ndigits)] = p2
            else:
                raise Exception('Search has not been successful in JMPR point placement.')

        net_graph.add_edge(p1, p2)
    return net_graph

def add_feeders_to_net_graph(points_approx, feeders_X, feeders_Y,
                           min_dist_radius,
                           max_dist_radius, points_set_rounding_ndigits):
    temp_len = feeders_X.shape[0]
    if temp_len <= 0 or temp_len != feeders_Y.shape[0]:
        raise Exception("Invalid input segments given for graph feeders.")

    key_func = lambda p_x, p_y, points_set_rounding_ndigits: str(round(p_x, points_set_rounding_ndigits)) + ',' + str(
        round(p_y, points_set_rounding_ndigits))

    feeders = []
    for i in range(temp_len):
        p1_key, r1 = get_closest_point_dynamically(feeders_X[i], feeders_Y[i], key_func, points_approx,
                                                   min_dist_radius,
                                                   max_dist_radius, points_set_rounding_ndigits,
                                                   step_size=0.1 ** points_set_rounding_ndigits)

        if p1_key is not None:
            feeders.append(points_approx[p1_key])
        else:
            raise Exception('Search has not been successful in feeder point placement.')

    return feeders

def get_isolated_switches_typed(points, switch_X, switch_Y):
    switches = []
    temp_len = switch_X.shape[0]
    if temp_len <= 0 or temp_len != switch_Y.shape[0]:
        raise Exception("Invalid input segments given for graph switches.")

    for i in range(temp_len):
        p1_key = str(switch_X[i]) + ',' + str(switch_Y[i])
        if p1_key not in points:
            print(bcolors.FAIL + 'Key not found in network\tX: {0:14} Y: {1:14}'.format(str(switch_X[i]),
                                                                                        str(switch_Y[
                                                                                                i])) + bcolors.ENDC)
            switches.append(Point(switch_X[i], switch_Y[i], 0))
    return switches


def get_isolated_switches(switches_dict, points):
    out = {}
    for key, array in switches_dict.items():
        out[key] = get_isolated_switches_typed(points, array[:, 0], array[:, 1])
    return out

class Network:
    def __init__(self, GRDMVL_path, HDMVL_path, JMPR_path, Feeder_path, CIRC_BRK_path, DISCNT_S_path, FUS_COUT_path, RECLOSER_path, RECLOSER_Select_path):
        GRDMVL = np.genfromtxt(GRDMVL_path, delimiter=',', skip_header=True)
        HDMVL = np.genfromtxt(HDMVL_path, delimiter=',', skip_header=True)
        JMPR = np.genfromtxt(JMPR_path, delimiter=',', skip_header=True)

        self.feeders = np.genfromtxt(Feeder_path, delimiter=',', skip_header=True)

        self.CIRC_BRK = np.genfromtxt(CIRC_BRK_path, delimiter=',', skip_header=True)
        self.DISCNT_S = np.genfromtxt(DISCNT_S_path, delimiter=',', skip_header=True)
        self.FUS_COUT = np.genfromtxt(FUS_COUT_path, delimiter=',', skip_header=True)
        self.RECLOSER = np.genfromtxt(RECLOSER_path, delimiter=',', skip_header=True)
        self.RECLOSER_Select = np.genfromtxt(RECLOSER_Select_path, delimiter=',', skip_header=True)

        HDMVL = np.r_[HDMVL, GRDMVL]

        # For ordinary lines
        segments = (HDMVL)[:, 1:]
        self.segments_start_x = segments[:, 0]
        self.segments_end_x = segments[:, 1]

        self.segments_start_y = segments[:, 2]
        self.segments_end_y = segments[:, 3]

        # For JMPRs
        JMPR_arr = JMPR[:, 1:]
        self.JMPR_start_x = JMPR_arr[:, 0]
        self.JMPR_end_x = JMPR_arr[:, 1]

        self.JMPR_start_y = JMPR_arr[:, 2]
        self.JMPR_end_y = JMPR_arr[:, 3]

    def get_feeder_points(self):
        return [Point(feeder[1], feeder[2], 0) for feeder in self.feeders]

    def get_buses(self):
        sys.setrecursionlimit(15000)
        POINTS_SET_ROUNDING_DIGITS = 1

        net_graph, points, points_approx = get_ordinary_net_graph(self.segments_start_x, self.segments_end_x,
                                                                  self.segments_start_y,
                                                                  self.segments_end_y, POINTS_SET_ROUNDING_DIGITS)
        net_graph = add_JMPRs_to_net_graph(net_graph, points, points_approx, self.JMPR_start_x, self.JMPR_end_x,
                                           self.JMPR_start_y,
                                           self.JMPR_end_y, 0.4, 4, POINTS_SET_ROUNDING_DIGITS)
        feeder_points = add_feeders_to_net_graph(points_approx, self.feeders[:, 1], self.feeders[:, 2], 0.4, 4, POINTS_SET_ROUNDING_DIGITS)
        #
        buses, branches, visited = net_graph.DFS(feeder_points)
        isolated_buses = net_graph.check_for_unmapped_buses(visited)

        out_buses = np.array([]).reshape((0, 2))
        for bus in buses:
            out_buses = np.r_[out_buses, [(bus.x, bus.y)]]

        out_branches = np.array([]).reshape((0, 4))
        for br in branches:
            out_branches = np.r_[out_branches, [(br[0].x, br[0].y, br[1].x, br[1].y)]]

        out_isolated_buses = np.array([]).reshape((0, 2))
        for bus in isolated_buses:
            out_isolated_buses = np.r_[out_isolated_buses, [(bus.x, bus.y)]]
            print(bcolors.FAIL + 'Bus not branched\tX: {0:14} Y: {1:14}'.format(str(bus.x),
                                                                                str(bus.y)) + bcolors.ENDC)
        print('{} isolated buses were detected.'.format(len(isolated_buses)))

        switches_dict = {
            "CIRC_BRK": self.CIRC_BRK,
            "DISCNT_S": self.DISCNT_S,
            "FUS_COUT": self.FUS_COUT,
            "RECLOSER": self.RECLOSER,
            "RECLOSER_Select":self.RECLOSER_Select
        }
        isolated_switches_dict = get_isolated_switches(switches_dict ,points)

        os.makedirs('out/switches')
        for switch_type, array in isolated_switches_dict.items():
            out_isolated_switches = np.array([]).reshape((0, 2))
            for switch in array:
                out_isolated_switches = np.r_[out_isolated_switches, [(switch.x, switch.y)]]
            np.savetxt('out/switches/isolated_' + switch_type + 's' + '.csv', out_isolated_switches, delimiter=',')



        os.makedirs('out/generic')
        np.savetxt('out/generic/buses.csv', out_buses, delimiter=',')
        np.savetxt('out/generic/branches.csv', out_branches, delimiter=',')
        np.savetxt('out/generic/isolated_buses.csv', out_isolated_buses, delimiter=',')
