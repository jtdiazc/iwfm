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
import pandas as pd
import sys
#Path to pywfm module
sys.path.insert(0, r'P:\Projects\5658_NSJWCD\IWRFM\PyWFM-master\PyWFM-master\src')
import pywfm
import iwfm
import os

def add_wells(gw_file,
              New_Wells,
              sm_pywfm,
              out_path,
              epsg_in=4326,
              epsg_out=26910,
              nlay=4,
              wells_flag="C       ID   HYDTYP   IOUTHL         X               Y         IOUTH        Name                      Comment",
              nouth_flag="/ NOUTH",
              output_suffix="_mod"):
    ''' add_wells() - Read IWFM Groundwater.dat file and add new wells

    Parameters
    ----------
    gw_file : str
        IWFM Groundwaer.dat file path (only for reading)
    New_Wells: Pandas dataframe with new wells (format of CASGEM Station.csv table)
    epsg_in: Reference system of wells in New_Wells dataframe
    nlay: number of layers in the model
    sm_pywfm: pywfm model object
    out_path: output path for the modified IWFM Groundwater.dat file
    epsg_out: reference system we are using in the IWFM model
    nlay: number of layers of the IWFM model
    wells_flag: flag of the line before the one where the wells start
    nouth_flag: flag of the line where the nouth variable is located
    output_suffix: suffix for the modified IWFM Groundwaer.dat file




    Returns
    -------
    New_Wells_mini: DataFrame with well names, coordinates and layers

    '''
    inProj = Proj(init='epsg:'+str(epsg_in))
    outProj = Proj(init='epsg:'+str(epsg_out))

    New_Wells['X'],New_Wells['Y']=transform(inProj, outProj, New_Wells['LONGITUDE'].values, New_Wells['LATITUDE'].values)

    #Let's add columns for stratigraphy
    New_Wells['top']=np.nan

    #Let's calculate screen top and bottom elevations
    New_Wells['screen_top']=New_Wells['GSE']-New_Wells['TOP_PRF']

    New_Wells['screen_bot'] = New_Wells['GSE'] - New_Wells['BOT_PRF']

    #Let's create columns where we will keep track of which are the layers where the wells are screened
    New_Wells['Layer']=''

    #Let's fix names
    New_Wells["Name"]=New_Wells.WELL_NAME
    New_Wells.loc[~New_Wells.SWN.isna(), "Name"] = New_Wells.loc[~New_Wells.SWN.isna(), "SWN"]

    #Let's drop wells for which we don't have screen depths
    #New_Wells = New_Wells[~(New_Wells.screen_top.isna() | New_Wells.screen_bot.isna())]

    for layer in range(nlay):
        New_Wells['lay_'+str(layer+1)+'_bot'] = np.nan

    New_Wells = New_Wells[~(New_Wells.screen_top.isna() | New_Wells.screen_bot.isna())]
    New_Wells=New_Wells.reset_index(drop=True)

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

            #Let's add 1 row per layer

        while len(New_Wells.loc[i,"Layer"])>1:
            new_row_dum=New_Wells.loc[i,:].copy()
            #Layer we will use for the new row
            new_row_dum["Layer"]=New_Wells.loc[i,"Layer"][-1]
            new_row_dum["Name"]=New_Wells.loc[i,"Name"]+"_L"+new_row_dum["Layer"]
            #Layer that will remain in the row we are iterating
            New_Wells.loc[i, "Layer"]=New_Wells.loc[i,"Layer"][:-1]
            #Let's add the new row ot the dataframe
            New_Wells = pd.concat([New_Wells,new_row_dum],ignore_index=True)

    New_Wells_mini=New_Wells[['Layer','X','Y','Name']].copy()

    #Let's import wells dataframe
    wells_df, nouth, GWHYDOUTFL, wells_gdf=iwfm.read_sim_wells_df(gw_file,sm_pywfm)

    #Let's import wells file
    lines = (open(gw_file).read().splitlines())

    #Let's find nouth variable
    lines_i = 0

    while lines[lines_i].find(nouth_flag) < 0:
        lines_i += 1
    lines_new = lines[0:lines_i]

    line_nouth=lines[lines_i].split()
    line_nouth[0]=str(nouth+New_Wells_mini.shape[0])
    line_nouth_str="    "+line_nouth[0]+"                           \t/ NOUTH"
    lines_new.append(line_nouth_str)

 #   with open(output_path, 'w') as f:
 #       for line in lines_new:
 #           f.write("%s\n" % line)

    i_s_2=lines_i + 1

    #Let's find where the wells section starts

    while lines[lines_i].find(wells_flag) < 0:
        lines_i += 1
    lines_i +=1

    #Let's advance to the last well
    lines_i += nouth+1
    #Let's copy this section to the new file
    for line in lines[i_s_2:lines_i]:
        lines_new.append(line)

 #   with open(output_path, 'w') as f:
 #       for line in lines_new:
 #           f.write("%s\n" % line)



    id_dum=nouth
    #Now, let's loop through the new wells
    for i in range(New_Wells_mini.shape[0]):
        id_dum+=1
        x_dum=str(round(New_Wells_mini.loc[i,'X'],4))
        y_dum = str(round(New_Wells_mini.loc[i, 'Y'], 3))
        name_dum=New_Wells_mini.loc[i, 'Name']
        layer_dum=New_Wells_mini.loc[i, 'Layer']
        line_dum=str(id_dum)+"\t0\t"+str(layer_dum)+"\t"+str(x_dum)+"\t"+str(y_dum)+"\t\t"+str(name_dum)+"\t\t/ Well #"+str(id_dum)+" Layer #"+str(layer_dum)
        lines_new.append(line_dum)

    for line in lines[lines_i:]:
        lines_new.append(line)

    #Let's create path to save file
    read_path_split=os.path.split(gw_file)
    input_name=read_path_split[-1]
    prefix=input_name[:input_name.find(".")]
    output_name=prefix+output_suffix+".dat"
    output_path=os.path.join(out_path,output_name)


    with open(output_path, 'w') as f:
        for line in lines_new:
            f.write("%s\n" % line)


    return New_Wells
