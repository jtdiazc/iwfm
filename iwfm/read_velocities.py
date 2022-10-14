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
import numpy as np
import pandas as pd
import sys
import os



def read_velocities(velocities_path,
                    sm_pywfm,
                    Centroids_Flag="*  ELEMENT                 X                 Y",
                    velocities_flag="*                              *          VELOCITIES AT CELL CENTROIDS          *",
                    time_flag="09/30/2020_24:00",
                    dir_out=r'P:\Projects\5658_NSJWCD\IWRFM\Output'):
    ''' read_velocities() -

    Parameters
    ----------

    Returns
    -------


    '''

    n_elements=16054

    lines = open(velocities_path).read().splitlines()


    #Let's find position of the centroids flag
    #index of element in list
    lines_i=0
    #Let's loop through elements of the list
    while lines[lines_i].find(Centroids_Flag)<0:
        lines_i+=1

    ##Let's create the dataframe of centroids
    centroids=pd.DataFrame(columns=["Element", "X", "Y"])
    #Let's add centroids
    lines_i += 1
    for i in range(n_elements):
        line_dum=lines[lines_i].split()
        centroids_dum = pd.DataFrame({"Element":[line_dum[0]],
                                      "X":[line_dum[1]],
                                      "Y":[line_dum[2]]})
        centroids=centroids.append(centroids_dum, ignore_index=True)
        lines_i+=1

    #Let's fix coordinates
    centroids["X"]=0.3048*centroids["X"].astype(float)
    centroids["Y"] = 0.3048 * centroids["Y"].astype(float)
    centroids["Element"] = centroids["Element"].astype(int)




    ##Let's find flag of velocities
    while lines[lines_i].find(velocities_flag)<0:
        lines_i+=1

    #Let's go to line with layers
    lines_i += 3
    layers=lines[lines_i].split()[2:]

    #Line of velocities
    lines_i += 1
    velocities = lines[lines_i].split()[3:]
    vel_list=["Lay{}_{}".format(a_, b_) for a_, b_ in zip(layers, velocities)]

    #Let's add columns to dataframe
    for i in range(len(vel_list)):
        centroids[vel_list[i]]=np.nan

    #Let's move to the timestep

    while lines[lines_i].find(time_flag)<0:
        lines_i+=1

    vel_dum=centroids.copy()
    #First line of timestep (element 1)
    line_dum = lines[lines_i].split()
    element_dum=int(line_dum[1])
    vel_dum.loc[vel_dum.Element == element_dum, vel_list] =line_dum[2:]
    lines_i+=1

    #Rest of elements
    for i in range(n_elements-1):
        line_dum=lines[lines_i].split()
        element_dum = int(line_dum[0])
        vel_dum.loc[vel_dum.Element == element_dum, vel_list] = line_dum[1:]
        lines_i += 1

    vel_dum.to_csv(os.path.join(dir_out,"Velocities.csv"))
#    wells_df['HYDROGRAPH ID']=wells_df['HYDROGRAPH ID'].astype(int)
#    hyd_df=hyd_df.join(wells_df.set_index('HYDROGRAPH ID'),on='HYDROGRAPH ID')


