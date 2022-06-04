import pandas as pd
import os


class MPC:
    def __init__(self, source_path):
        self.bus = pd.read_csv(os.path.join(source_path, 'mpc_bus.csv'), header=None, dtype=float)
        self.branch = pd.read_csv(os.path.join(source_path, 'mpc_branch.csv'), header=None, dtype=float)
        self.branch_fault_allocation_time = pd.read_csv(
            os.path.join(source_path, 'mpc_branch_fault_allocation_time.csv'), header=None, dtype=float)
        self.branch_reliability = pd.read_csv(os.path.join(source_path, 'mpc_branch_reliability.csv'), header=None,
                                              dtype=float)
        self.bus_load_factor = pd.read_csv(os.path.join(source_path, 'mpc_bus_load_factor.csv'), header=None,
                                           dtype=float)
        self.bus_xy = pd.read_csv(os.path.join(source_path, 'mpc_bus_xy.csv'), header=None, dtype=float)
        self.gen = pd.read_csv(os.path.join(source_path, 'mpc_gen.csv'), header=None, dtype=float)
        self.gencost = pd.read_csv(os.path.join(source_path, 'mpc_gencost.csv'), header=None, dtype=float)
        self.list = pd.read_csv(os.path.join(source_path, 'mpc_list.csv'), header=None, dtype=float)
        self.load_weight = pd.read_csv(os.path.join(source_path, 'mpc_load_weight.csv'), header=None, dtype=float)
        pass
