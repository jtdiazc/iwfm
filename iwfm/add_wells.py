# read_wells.py
# Reads from Groundwater.dat file and builds a dictionary of groundwater hydrograph
# info and gwhyd_sim columns, and returns the dictionary
# Copyright (C) 2020-2021 University of California
# -----------------------------------------------------------------------------
# This information is free; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This work is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# For a copy of the GNU General Public License, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
# -----------------------------------------------------------------------------
from pyproj import Proj, transform
import numpy as np
#Path to pywfm module
sys.path.insert(0, r'P:\Projects\5658_NSJWCD\IWRFM\PyWFM-master\PyWFM-master\src')
import pywfm

def add_wells(gw_file,New_Wells,sm_pywfm,epsg_in=4326,epsg_out=26910,nlay=4):
    ''' read_wells() - Read IWFM Groundwater.dat file and build a dictionary
        of groundwater hydrograph info and gwhyd_sim columns

    Parameters
    ----------
    gw_file : str
        IWFM Groundwaer.dat file path (only for reading)
    New_Wells: Pandas dataframe with new wells (format of CASGEM Station.csv table)
    epsg_in: Reference system of wells in New_Wells dataframe
    nlay: number of layers in the model
    sm_pywfm: pywfm model object

    Returns
    -------
    well_dict : dictionary
        key = well name (i.e. state ID), values = simulated heads

    '''
    inProj = Proj(init='epsg:'+str(epsg_in))
    outProj = Proj(init='epsg:'+str(epsg_out))

    New_Wells['X'],New_Wells['Y']=transform(inProj, outProj, New_Wells['LONGITUDE'], New_Wells['LATITUDE'])

    #Let's add columns for stratigraphy
    New_Wells['top']=np.nan

    #Let's calculate screen top and bottom elevations
    New_Wells['screen_top']=New_Wells['GSE']-New_Wells['TOP_PRF']

    New_Wells['screen_bot'] = New_Wells['GSE'] - New_Wells['BOT_PRF']

    #Let's create columns where we will keep track of which are the layers where the wells are screened
    New_Wells['Layer']=''

    for layer in range(nlay):
        New_Wells['lay_'+str(layer+1)+'_bot'] = np.nan

    #Now, let's get lithology from DLL

    #Let's loop through wells
    for i in range(New_Wells.shape[0]):
        lith_dum=sm_pywfm.get_stratigraphy_atXYcoordinate(New_Wells.loc[i,'X'], New_Wells.loc[i,'Y'],3.2808)
        New_Wells.loc[i,'top']=lith_dum[0]
        for layer in range(nlay):
            New_Wells.loc[i,'lay_' + str(layer + 1) + '_bot'] = lith_dum[layer + 1]

            #Is the well screened in this layer?
            #Top layer
            if layer==0 and New_Wells.loc[i,'screen_top']>=New_Wells.loc[i,'lay_' + str(layer + 1) + '_bot']:
                New_Wells.loc[i, 'Layer']=New_Wells.loc[i,'Layer']+str(layer+1)
            #Rest of the layers
            if layer > 0:
                #The screen will be in the layer in all the cases except when both the top and bottom of the screen are above
                #or below the layer
                if not ((New_Wells.loc[i,'screen_top']>New_Wells.loc[i,'lay_' + str(layer) + '_bot'] and
                    New_Wells.loc[i,'screen_bot']>New_Wells.loc[i,'lay_' + str(layer) + '_bot']) or
                    (New_Wells.loc[i,'screen_top']<New_Wells.loc[i,'lay_' + str(layer + 1) + '_bot'] and
                    New_Wells.loc[i, 'screen_bot'] < New_Wells.loc[i, 'lay_' + str(layer + 1) + '_bot'])):
                    New_Wells.loc[i, 'Layer'] = New_Wells.loc[i, 'Layer'] + str(layer + 1)




    return
