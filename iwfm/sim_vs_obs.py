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
import iwfm




def sim_vs_obs(OBS,gwhyd_sim):
    ''' sim_vs_obs() - draws a scatterplot of observed vs simulated values

    Parameters
    ----------
    OBS: Pandas dataframe with observations. Date in "Date" column
    gwhyd_sim: Pandas dataframe with simulated time series (output of read_sim_hyds_df)


    Returns
    -------





    '''

    #First, let's match obs and sim records for same well, month, and year
    iwfm.match_obs_sim(OBS,gwhyd_sim)


    return

