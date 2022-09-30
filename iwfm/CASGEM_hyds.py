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
import sys

sys.path.insert(0, r'P:\Projects\5658_NSJWCD\IWRFM\pyemu')
#Let's add pyemu
import pyemu

def CASGEM_hyds(gwe_path,wells_df,gwhyd_sim,dir_out,sim_period):
    ''' read_sim_hyds() - Read simulated values from multiple IWFM output 
        hydrograph files into Pandas dataframe

    Parameters
    ----------
    gwe_path : Path to CASGEM "GroundwaterElevation.csv" table


    wells_df: Pandas dataframe with wells (output of read_sim_wells_df function)

    dir_out: Directory where hydrographs plots will be saved

    sim_period: Data Frame containing date of start of simulation in the first rown and date of end in the
    second row. One colunm called Date

    Returns
    -------
    IWFM_in_CASGEM: Wells in the IWFM model which are also in the CASGEM csv file

    IWFM_not_in_CASGEM: Wells in the IWFM model which are not in the CASGEM csv file

    CASGEM_not_in_IWFM: Wells in the CASGEM csv file which are not in the IWFM model

    OBS: observations
    

    '''

    #Let's import gwe timeseries to pandas dataframe
    gwl = pd.read_csv(gwe_path)

    #Let's find wells that are both in CASGEM and the IWFM model
    IWFM_in_CASGEM = wells_df.Name[wells_df.Name.isin(gwl.SWN)|(wells_df.Name.isin(gwl.WELL_NAME ))].reset_index(drop=True)

    #Let's match wells where the base and meridian of the state code was omitted in the IWFM model
    bm_omitted=wells_df.Name[wells_df.Name.isin(gwl.SWN[gwl.SWN.str.len() == 13].str.slice(stop=-1))].reset_index(drop=True)
    bm_omitted=bm_omitted[~bm_omitted.isin(IWFM_in_CASGEM)]

    if len(bm_omitted)>0:
    #Let's retrieve the original CASGEM names
        bm_omit = pd.DataFrame()
        bm_omit['SWN'] = gwl.SWN[gwl.SWN.str.len() == 13].unique()
        bm_omit['IWFM']=gwl.SWN[gwl.SWN.str.len() == 13].str.slice(stop=-1).unique()
        bm_omit=bm_omit[bm_omit.IWFM.isin(bm_omitted)].reset_index(drop=True)

        #Let's loop through wells and fix names in CASGEM hydrographs data frame
        for well in bm_omitted:
            gwl.loc[gwl.SWN==bm_omit[bm_omit.IWFM==well].SWN[0],'SWN']=bm_omit[bm_omit.IWFM==well].reset_index(drop=True).IWFM[0]
            IWFM_in_CASGEM=IWFM_in_CASGEM.append(bm_omit[bm_omit.IWFM==well].IWFM,ignore_index=True)

    #Let's clean by different combinations of upper and lower casing
    low_case_match=wells_df.Name[wells_df.Name.str.lower().isin(gwl.WELL_NAME.str.lower())]
    low_case_match=low_case_match[~low_case_match.isin(IWFM_in_CASGEM)].reset_index(drop=True)

    if len(low_case_match) > 0:
        # Let's retrieve the original CASGEM names
        lc_match = pd.DataFrame()
        lc_match['WELL_NAME']=gwl.WELL_NAME[gwl.WELL_NAME.str.lower().isin(low_case_match.str.lower())].unique()
        lc_match['IWFM']=wells_df.Name[pd.Index(wells_df.Name).str.lower().get_indexer(lc_match['WELL_NAME'].str.lower())].reset_index(drop=True)

        # Let's loop through wells and fix names in CASGEM hydrographs data frame
        for well in low_case_match:
            gwl.loc[gwl.WELL_NAME == lc_match[lc_match.IWFM == well].reset_index(drop=True).WELL_NAME[0], 'WELL_NAME'] = lc_match[lc_match.IWFM == well].reset_index(drop=True).IWFM[0]
            IWFM_in_CASGEM = IWFM_in_CASGEM.append(lc_match[lc_match.IWFM == well].IWFM, ignore_index=True)
    # Let's find wells that are in the IWFM model, but not in CASGEM

    IWFM_not_in_CASGEM=wells_df.Name[~wells_df.Name.isin(IWFM_in_CASGEM)]

    #Let's find wells that are in CASGEM, but not in the IWFM model
    CASGEM_not_in_IWFM=gwl.SWN[~gwl.SWN.isin(IWFM_in_CASGEM)].dropna().append(gwl.WELL_NAME[~gwl.WELL_NAME.isin(IWFM_in_CASGEM)]).unique()
    
    #Let's remove nans
    CASGEM_not_in_IWFM=CASGEM_not_in_IWFM[~pd.isnull(CASGEM_not_in_IWFM)]

    CASGEM_not_in_IWFM=CASGEM_not_in_IWFM[~np.isin(CASGEM_not_in_IWFM, bm_omit['SWN'])]
    CASGEM_not_in_IWFM[~np.isin(CASGEM_not_in_IWFM, lc_match['WELL_NAME'])]
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

    #Let's subset now all the observations that will be useful
    OBS=gwl[gwl.WELL_NAME.isin(IWFM_in_CASGEM)|gwl.SWN.isin(IWFM_in_CASGEM)].copy().reset_index(drop=True)

    #Now, let's filter for records which are in the simulation period of the model
    OBS=OBS[(OBS.Date >= sim_period.loc[0, 'Date']) & (OBS.Date <= sim_period.loc[1, 'Date'])].reset_index(drop=True)

    #Let's remove rows for which we don't have water level records
    OBS=OBS[~OBS.WSE.isnull()].reset_index(drop=True)

    #Let's fix names
    OBS['Name']=""
    OBS.loc[OBS.WELL_NAME.isin(IWFM_in_CASGEM), "Name"] = OBS.loc[OBS.WELL_NAME.isin(IWFM_in_CASGEM), "WELL_NAME"]
    OBS.loc[(OBS.SWN.isin(IWFM_in_CASGEM)) & (OBS.Name == ""), "Name"] = OBS.loc[
        (OBS.SWN.isin(IWFM_in_CASGEM)) & (OBS.Name == ""), "SWN"]

    return IWFM_in_CASGEM, IWFM_not_in_CASGEM, CASGEM_not_in_IWFM, OBS

