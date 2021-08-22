from ens.helper.helper import *
from ens.helper.MPC import MPC
from ens.optimization.optimize_ens1 import optimize_ens

clearc()
mpc_obj = MPC('cases/case33bw')
livebus_loc = [1, 18, 22, 25, 33]
livebus_auto = [1, 1, 0, 0, 0]

sw_recloser_exist = [1]
sw_sectionalizer_exist = []
sw_sectioner_automatic_exist = []
sw_sectioner_manual_exist = []
sw_cutout_exist = []
current_xy = [-10,- 10]
speed = 50

num_of_new_reclosers = 3
num_of_new_sectionalizers = 0
num_of_new_automatic_sectioners = 2
num_of_new_manual_sectioners = 0
num_of_new_cutouts = 0


res  = optimize_ens(mpc_obj,livebus_loc, livebus_auto, sw_recloser_exist, sw_sectionalizer_exist, sw_sectioner_automatic_exist, sw_sectioner_manual_exist, sw_cutout_exist, current_xy, speed, num_of_new_reclosers, num_of_new_sectionalizers, num_of_new_automatic_sectioners, num_of_new_manual_sectioners, num_of_new_cutouts)

print(res)