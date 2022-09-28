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
import os
import numpy as np


def CASGEM_hyds(gwe_path,wells_df,gwhyd_sim,dir_out):
    ''' read_sim_hyds() - Read simulated values from multiple IWFM output 
        hydrograph files into Pandas dataframe

    Parameters
    ----------
    gwe_path : Path to CASGEM "GroundwaterElevation.csv" table


    wells_df: Pandas dataframe with wells (output of read_sim_wells_df function)

    dir_out: Directory where hydrographs plots will be saved

    Returns
    -------
    IWFM_in_CASGEM: Wells in the IWFM model which are also in the CASGEM csv file

    IWFM_not_in_CASGEM: Wells in the IWFM model which are not in the CASGEM csv file

    CASGEM_not_in_IWFM: Wells in the CASGEM csv file which are not in the IWFM model
    

    '''

    #Let's import gwe timeseries to pandas dataframe
    gwl = pd.read_csv(gwe_path)

    #Let's find wells that are both in CASGEM and the IWFM model
    IWFM_in_CASGEM = wells_df.Name[wells_df.Name.isin(gwl.SWN)|(wells_df.Name.isin(gwl.WELL_NAME ))].reset_index(drop=True)

    # Let's find wells that are in the IWFM model, but not in CASGEM

    IWFM_not_in_CASGEM=wells_df.Name[~wells_df.Name.isin(IWFM_in_CASGEM)]

    #Let's find wells that are in CASGEM, but not in the IWFM model
    CASGEM_not_in_IWFM=gwl.SWN[~gwl.SWN.isin(IWFM_in_CASGEM)].dropna().append(gwl.WELL_NAME[~gwl.WELL_NAME.isin(IWFM_in_CASGEM)]).unique()
    

    #Let's convert dates of gwl to Pandas format
    gwl["Date"]=pd.to_datetime(gwl.MSMT_DATE.str[:-11], format="%Y/%m/%d")

    #Let's loop through wells for which we have both simulations and observations
    for well in IWFM_in_CASGEM:
        #Let's plot hydrographs
        ax = gwl[((gwl.SWN==well)|(gwl.WELL_NAME==well))&
                 (gwl.Date>=min(gwhyd_sim.Date))&
                 (gwl.Date<=max(gwhyd_sim.Date))].plot(x='Date',
                                                       y='WSE',
                                                       marker='o',
                                                       linestyle = 'None',
                                                       title=well)
        gwhyd_sim[gwhyd_sim.Name==well].plot(ax=ax, x='Date', y='SIM')
        fig = ax.get_figure()
        fig.savefig(os.path.join(dir_out,well+".png"))

    return IWFM_in_CASGEM, IWFM_not_in_CASGEM, CASGEM_not_in_IWFM

