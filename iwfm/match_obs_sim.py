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
import sys
sys.path.insert(0, r'P:\Projects\5658_NSJWCD\IWRFM\iwfm')
#Let's import iwfm
import iwfm



def match_obs_sim(OBS,
                  gwhyd_sim,
                  keys=["Name",
                        "Month",
                        "Year"]):
    ''' match_obs_sim - matches observations and simulated values for the same month and year

    Parameters
    ----------
    OBS: Pandas dataframe with observations. Date in "Date" column
    gwhyd_sim: Pandas dataframe with simulated time series (output of read_sim_hyds_df)
    keys: columns to match when joining dataframes


    Returns
    -------

    OBS_SIM: Pandas dataframe with OBS and SIM for joined rows





    '''

    #First, lets add columns with year and month values

    OBS["Year"]=OBS.Date.dt.year
    OBS["Month"] = OBS.Date.dt.month


    gwhyd_sim["Year"]=gwhyd_sim.Date.dt.year
    gwhyd_sim["Month"] = gwhyd_sim.Date.dt.month

    OBS_SIM=pd.merge(OBS, gwhyd_sim, on=keys, how='inner')



    return OBS_SIM

