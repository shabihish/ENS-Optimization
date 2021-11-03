from ext import *
import os

graph_constructor = Network(os.path.join('data/attrib_tabl/GRDMVL.csv'),
                            os.path.join('data/attrib_tabl/HDMVL.csv'),
                            os.path.join('data/attrib_tabl/JMPR.csv'))
graph_constructor.get_buses()
