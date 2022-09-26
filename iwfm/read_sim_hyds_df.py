# read_sim_hyds.py
# Read simulated hydrographs from IWFM hydrograph.out file
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

import pandas as pd

def read_sim_hyds_df(nhyds, gwhyd_files):
    ''' read_sim_hyds() - Read simulated values from multiple IWFM output 
        hydrograph files into Pandas dataframe

    Parameters
    ----------
    nhyds : int
        number of simulated hydrograph files
    
    gwhyd_files : list
        list of input file names

    Returns
    -------
    gwhyd_sim : list
        list with one item of hydrograph values for each input hydrograph file

    '''
    gwhyd_sim = []

    for k in range(0, nhyds):
        gwhyd_lines = (open(gwhyd_files[k]).read().splitlines())
        #gwhyd_lines = [word.replace('_24:00', ' ') for word in gwhyd_lines]

        #Let's find position of "Hydrograph ID" flag
        #index of element in list
        lines_i=0
        #Let's loop through elements of the list
        while gwhyd_lines[lines_i].find("HYDROGRAPH ID")<0:
            lines_i+=1
        ##Let's create the dataframe with IDs
        hyd_df=pd.DataFrame({"HYDROGRAPH ID":[int(i) for i in gwhyd_lines[lines_i].split()[3:]]})

        ##Let's find flag of layers
        while gwhyd_lines[lines_i].find("LAYER")<0:
            lines_i+=1

        #We add to the dataframe layer numbers
        hyd_df["LAYER"]=[int(i) for i in gwhyd_lines[lines_i].split()[2:]]

        ##Let's find flag of nodes
        while gwhyd_lines[lines_i].find("NODE")<0:
            lines_i+=1

        #We add to the dataframe node numbers
        hyd_df["NODE"]=[int(i) for i in gwhyd_lines[lines_i].split()[2:]]

        ##Let's find flag of elements
        while gwhyd_lines[lines_i].find("ELEMENT")<0:
            lines_i+=1

        #We add to the dataframe element numbers
        hyd_df["ELEMENT"]=[int(i) for i in gwhyd_lines[lines_i].split()[2:]]

        #This will be the template for all the hydrographs
        hyd_df_temp=hyd_df

        ##Let's find flag of times
        while gwhyd_lines[lines_i].find("TIME")<0:
            lines_i+=1

        #Advance one line
        lines_i += 1

        #Let's add the first hydrograph
        #Let's add time
        hyd_df["TIME"]=gwhyd_lines[lines_i].split()[0]
        #Let's add the heads
        hyd_df["HEAD"]=[float(i) for i in gwhyd_lines[lines_i].split()[1:]]

        #Advance one line
        lines_i += 1

        #Now, let's add the rest of the hydrographs
        while lines_i<len(gwhyd_lines):
            #Dummy template
            hyd_df_dum=hyd_df_temp.copy()
            hyd_df_dum["TIME"] = gwhyd_lines[lines_i].split()[0]
            hyd_df_dum["SIM"] = [float(i) for i in gwhyd_lines[lines_i].split()[1:]]
            hyd_df=pd.concat([hyd_df, hyd_df_dum], ignore_index=True)

            lines_i += 1

    #Let's convert dates to Pandas date format
    hyd_df["Date"] = pd.to_datetime(hyd_df["TIME"].str[:-6], format="%m/%d/%Y")

    return hyd_df
