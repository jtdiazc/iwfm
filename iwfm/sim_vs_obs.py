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
import sklearn.metrics
import os




def sim_vs_obs(OBS,gwhyd_sim,dir_out):
    ''' sim_vs_obs() - draws a scatterplot of observed vs simulated values

    Parameters
    ----------
    OBS: Pandas dataframe with observations. Date in "Date" column
    gwhyd_sim: Pandas dataframe with simulated time series (output of read_sim_hyds_df)
    dir_out: Directory where the scatter plot will be saved


    Returns
    -------





    '''

    #First, let's match obs and sim records for same well, month, and year

    OBS_SIM=iwfm.match_obs_sim(OBS,gwhyd_sim)

    ax = OBS_SIM.plot.scatter(x='WSE', y='SIM')
    ax.axline((1, 1), slope=1, color='g')

    #Let's calculate r2
    r2=sklearn.metrics.r2_score(OBS_SIM['WSE'],OBS_SIM['SIM'])

    ax.text(max(max(OBS_SIM.WSE),max(OBS_SIM.SIM))-15, max(max(OBS_SIM.WSE),max(OBS_SIM.SIM))-5, "r2= "+str(round(r2,2)))

    #Let's set axis limits
    ax.set_xlim(min(min(OBS_SIM.WSE),min(OBS_SIM.SIM)),max(max(OBS_SIM.WSE),max(OBS_SIM.SIM)))
    ax.set_ylim(min(min(OBS_SIM.WSE), min(OBS_SIM.SIM)), max(max(OBS_SIM.WSE), max(OBS_SIM.SIM)))
    fig = ax.get_figure()
    fig.savefig(os.path.join(dir_out,"OBS_vs_SIM.png"))

    #Let's also print scatter plots for each well

    for well in OBS_SIM.Name.unique():
        OBS_SIM_dum=OBS_SIM[OBS_SIM.Name==well].copy()
        ax = OBS_SIM_dum.plot.scatter(x='WSE', y='SIM',title=well)
        ax.axline((1, 1), slope=1, color='g')

        # Let's calculate r2
        r2 = sklearn.metrics.r2_score(OBS_SIM_dum['WSE'], OBS_SIM_dum['SIM'])

        ax.text(max(max(OBS_SIM_dum.WSE), max(OBS_SIM_dum.SIM)) - 15, max(max(OBS_SIM_dum.WSE), max(OBS_SIM_dum.SIM)) - 5,
                "r2= " + str(round(r2, 2)))

        # Let's set axis limits
        ax.set_xlim(min(min(OBS_SIM_dum.WSE), min(OBS_SIM_dum.SIM))-5, max(max(OBS_SIM_dum.WSE), max(OBS_SIM_dum.SIM))+5)
        ax.set_ylim(min(min(OBS_SIM_dum.WSE), min(OBS_SIM_dum.SIM))-5, max(max(OBS_SIM_dum.WSE), max(OBS_SIM_dum.SIM))+5)
        fig = ax.get_figure()
        fig.savefig(os.path.join(dir_out, "OBS_vs_SIM_"+well+".png"))

    return


