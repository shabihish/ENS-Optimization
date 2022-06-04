from ext import *
import os

graph_constructor = Network(os.path.join('data/attrib_tabl/GRDMVL.csv'),
                            os.path.join('data/attrib_tabl/HDMVL.csv'),
                            os.path.join('data/attrib_tabl/JMPR.csv'),
                            os.path.join('data/attrib_tabl/Feeder.csv'),
                            os.path.join('data/attrib_tabl/CIRC_BRK.csv'),
                            os.path.join('data/attrib_tabl/DISCNT_S.csv'),
                            os.path.join('data/attrib_tabl/FUS_COUT.csv'),
                            os.path.join('data/attrib_tabl/RECLOSER.csv'),
                            os.path.join('data/attrib_tabl/RECLOSER_Select.csv'))
graph_constructor.get_buses()
