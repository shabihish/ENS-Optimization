import numpy as np
import pandas as pd
import sys
from netgraph import *


class Network:
    def __init__(self, GRDMVL_path, HDMVL_path, JMPR_path):
        GRDMVL = pd.read_csv(GRDMVL_path)
        HDMVL = pd.read_csv(HDMVL_path)
        JMPR = pd.read_csv(JMPR_path)

        HDMVL.append(GRDMVL)
        HDMVL.append(JMPR)

        segments = (HDMVL.to_numpy())[:, 1:]
        self.segments_start_x = segments[:, 0]
        self.segments_end_x = segments[:, 1]

        self.segments_start_y = segments[:, 2]
        self.segments_end_y = segments[:, 3]

    def get_buses(self):
        sys.setrecursionlimit(15000)
        temp_len = self.segments_end_y.shape[0]
        if temp_len <= 0 or temp_len != self.segments_start_y.shape[0] or temp_len != self.segments_start_x.shape[
            0] or temp_len != \
                self.segments_end_x.shape[0]:
            raise Exception("Invalid input segments given for graph construction.")

        net_graph = NetGraph()
        points = {}
        for i in range(temp_len):
            p1_key = str(self.segments_start_x[i]) + ',' + str(self.segments_start_y[i])
            p2_key = str(self.segments_end_x[i]) + ',' + str(self.segments_end_y[i])
            if p1_key not in points:
                p1 = Point(self.segments_start_x[i], self.segments_start_y[i])
                points[p1_key] = p1
            else:
                p1 = points[p1_key]

            if p2_key not in points:
                p2 = Point(self.segments_end_x[i], self.segments_end_y[i])
                points[p2_key] = p2
            else:
                p2 = points[p2_key]

            net_graph.add_edge(p1, p2)

        buses = net_graph.DFS()

        out_buses = np.array([]).reshape((0, 2))
        for bus in buses:
            out_buses = np.r_[out_buses, [(bus.x, bus.y)]]
        np.savetxt('buses.csv', out_buses, delimiter=',')
