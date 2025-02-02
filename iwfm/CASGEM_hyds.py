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
import matplotlib.pyplot as plt
import sklearn.metrics

sys.path.insert(0, r'P:\Projects\5658_NSJWCD\IWRFM\pyemu')
#Let's add pyemu
import pyemu

def CASGEM_hyds(gwe_path,wells_df,gwhyd_sim,dir_out,sim_period,y_range,stations_path,sm_pywfm,well_reference="RPE"):
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

    stations = pd.read_csv(stations_path)

    #Number of model layers
    nlay=sm_pywfm.get_n_layers()

    #Simulation dates
    sim_start=sm_pywfm.get_time_specs()[0][0]
    sim_end = sm_pywfm.get_time_specs()[0][-1]

    #Simulation dates in Dataframe
    sim_dates=pd.DataFrame({'Date_raw':[sim_start,sim_end]})
    sim_dates["Date"]=sim_dates.Date_raw.str[:-6]
    sim_dates["Date"]=pd.to_datetime(sim_dates.Date)

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
            IWFM_in_CASGEM=pd.concat([IWFM_in_CASGEM,bm_omit[bm_omit.IWFM==well].IWFM],ignore_index=True)

    #Let's clean by different combinations of upper and lower casing
    low_case_match=wells_df.Name[wells_df.Name.str.lower().isin(gwl.WELL_NAME.str.lower())]
    low_case_match=low_case_match[~low_case_match.isin(IWFM_in_CASGEM)].reset_index(drop=True)

    if len(low_case_match) > 0:
        # Let's retrieve the original CASGEM names
        names_dum = pd.DataFrame({'Name': wells_df.Name.unique()})
        lc_match = pd.DataFrame()
        lc_match['WELL_NAME']=gwl.WELL_NAME[gwl.WELL_NAME.str.lower().isin(low_case_match.str.lower())].unique()

        lc_match['IWFM'] = names_dum.Name[
            pd.Index(names_dum.Name).str.lower().get_indexer(lc_match['WELL_NAME'].str.lower())].reset_index(drop=True)

        # Let's loop through wells and fix names in CASGEM hydrographs data frame
        for well in low_case_match:
            gwl.loc[gwl.WELL_NAME == lc_match[lc_match.IWFM == well].reset_index(drop=True).WELL_NAME[0], 'WELL_NAME'] = lc_match[lc_match.IWFM == well].reset_index(drop=True).IWFM[0]
            IWFM_in_CASGEM = pd.concat([IWFM_in_CASGEM,lc_match[lc_match.IWFM == well].IWFM], ignore_index=True)
    # Let's find wells that are in the IWFM model, but not in CASGEM

    IWFM_not_in_CASGEM=wells_df.Name[~wells_df.Name.isin(IWFM_in_CASGEM)]

    #Let's find wells that are in CASGEM, but not in the IWFM model
    CASGEM_not_in_IWFM=pd.concat([gwl.SWN[~gwl.SWN.isin(IWFM_in_CASGEM)].dropna(),gwl.WELL_NAME[~gwl.WELL_NAME.isin(IWFM_in_CASGEM)]]).unique()
    
    #Let's remove nans
    CASGEM_not_in_IWFM=CASGEM_not_in_IWFM[~pd.isnull(CASGEM_not_in_IWFM)]
    if len(bm_omitted) > 0:
        CASGEM_not_in_IWFM=CASGEM_not_in_IWFM[~np.isin(CASGEM_not_in_IWFM, bm_omit['SWN'])]
    if len(low_case_match) > 0:
        CASGEM_not_in_IWFM[~np.isin(CASGEM_not_in_IWFM, lc_match['WELL_NAME'])]
    #Let's convert dates of gwl to Pandas format
    gwl["Date"]=pd.to_datetime(gwl.MSMT_DATE.str[:-11], format="%Y-%m-%d")

    #List with ranges of hydrographs
    ranges= {}

    #We'll add screen information to wells df
    wells_df["Screen_top"]=np.nan
    wells_df["Screen_bot"] = np.nan

    wells_df["IOUTHL"]=wells_df["IOUTHL"].astype(int)
    wells_df["HYDROGRAPH ID"] = wells_df["HYDROGRAPH ID"].astype(int)

    IWFM_in_CASGEM=IWFM_in_CASGEM.unique()

    CASGEM_outside_range = []
    
    #Let's loop through wells for which we have both simulations and observations
    for well in IWFM_in_CASGEM:
        #Let's grab well information
        station_dum=stations[(stations.WELL_NAME==well)|(stations.SWN==well)|(stations.WELL_NAME.str.find(well)>=0)].reset_index(drop=True)
        screen_top_dum=station_dum.loc[0,well_reference] - station_dum.loc[0,'TOP_PRF']
        screen_bot_dum = station_dum.loc[0, well_reference] - station_dum.loc[0, 'BOT_PRF']
        screen_length_dum=screen_top_dum-screen_bot_dum
        well_bot_dum=station_dum.loc[0, well_reference] - station_dum.loc[0, 'WELL_DEPTH']
        well_depth_dum=station_dum.loc[0, 'WELL_DEPTH']
        wells_dum=wells_df[wells_df.Name == well].reset_index(drop=True)
        wells_df.loc[wells_df.Name == well,"Screen_top"]=screen_top_dum
        wells_df.loc[wells_df.Name == well, "Screen_bot"] = screen_bot_dum
        gwl_dum=gwl[(gwl.SWN==well)|(gwl.WELL_NAME==well)]
        gwl_dum=gwl_dum[(gwl_dum.Date >= sim_dates.loc[0, "Date"]) & (gwl_dum.Date <= sim_dates.loc[1, "Date"])].reset_index(drop=True)
        top_dum=wells_dum.Top.unique()[0]

        ## Skip CASGEM wells that don't have data within simulation period
        if gwl_dum.WSE.isnull().all():
            CASGEM_outside_range.append(well)
            continue

        
        #Let's retrieve which hydrographs we will need
        IDs_dum=[]
        #List with weights
        w=[]
        #Do we have nan in screen values?
        if (np.isnan(screen_top_dum)|np.isnan(screen_bot_dum)):
            #Do we also have nan in well depth
            if np.isnan(well_depth_dum):
                    #In this case, we add all the layers

                for i in range(nlay):
                    # In this case, we add all the layers
                    IDs_dum.append(wells_dum.loc[wells_dum.IOUTHL == i + 1, "HYDROGRAPH ID"].values[0])
                    # Bottom of the layer
                    bot_lay_dum = wells_dum.loc[0, "L" + str(i + 1) + "_bot"]
                    if i == 0:
                        # Surface elevation
                        top_lay_dum = wells_dum.loc[0, 'Top']
                    else:
                        top_lay_dum = wells_dum.loc[0, "L" + str(i) + "_bot"]
                    lay_length=top_lay_dum-bot_lay_dum
                    w.append(lay_length)
                # Let's normalize weights
                Model_Depth=wells_dum.loc[0, 'Top']-bot_lay_dum
                w=[x / (wells_dum.loc[0, 'Top']-bot_lay_dum) for x in w]

            else:
            #In this case, we add all the layers included within the well depth
                for i in range(nlay):
                    #Bottom of the layer
                    bot_lay_dum = wells_dum.loc[0, "L" + str(i + 1) + "_bot"]
                    #If the top of the layer is above the bottom of the well, we will add the layer to the list
                    #Layer 1
                    if i==0:
                        #Surface elevation
                        top_lay_dum=wells_dum.loc[0,'Top']
                        IDs_dum.append(wells_dum.loc[wells_dum.IOUTHL == i + 1, "HYDROGRAPH ID"].values[0])
                        #Let's add weight
                        #Length of layer in well
                        lay_length=min(top_dum-bot_lay_dum,top_dum-well_bot_dum)
                        w.append(lay_length)
                    else:
                        # Top of layer
                        top_lay_dum = wells_dum.loc[0, "L" + str(i) + "_bot"]
                        if (top_lay_dum>well_bot_dum):
                            if len(wells_dum.loc[wells_dum.IOUTHL == i + 1, "HYDROGRAPH ID"].values) > 0:
                                IDs_dum.append(wells_dum.loc[wells_dum.IOUTHL == i + 1, "HYDROGRAPH ID"].values[0])
                                lay_length = min(top_lay_dum - bot_lay_dum, top_lay_dum - well_bot_dum)
                                w.append(lay_length)
                # Let's normalize weights
                w = w / well_depth_dum


        else:
            #Let's loop through layers
            for i in range(nlay):
                #Bottom of the layer
                bot_lay_dum = wells_dum.loc[0, "L" + str(i + 1) + "_bot"]
                #Is the well screened in the layer?
                #First we see layer one
                if i==0:
                    if ~(screen_top_dum<bot_lay_dum):
                        IDs_dum.append(wells_dum.loc[wells_dum.IOUTHL==1,"HYDROGRAPH ID"].values[0])
                        #Let's add weight
                        lay_length = min(screen_top_dum - bot_lay_dum, top_dum - bot_lay_dum,screen_top_dum - screen_bot_dum)
                        w.append(lay_length)
                #For the rest of the layers
                else:
                    #Top of layer
                    top_lay_dum=wells_dum.loc[0, "L" + str(i ) + "_bot"]
                    #Bottom of the layer
                    bot_lay_dum=wells_dum.loc[0, "L" + str(i+1) + "_bot"]
                    #If screen is in the layer
                    if~((screen_top_dum<bot_lay_dum)|(screen_bot_dum>top_lay_dum)):
                        if len(wells_dum.loc[wells_dum.IOUTHL == i + 1, "HYDROGRAPH ID"].values) > 0:
                            IDs_dum.append(wells_dum.loc[wells_dum.IOUTHL == i+1, "HYDROGRAPH ID"].values[0])
                            #Let's add weight
                            lay_length = min(screen_top_dum - bot_lay_dum, top_lay_dum - bot_lay_dum,screen_top_dum - screen_bot_dum,top_lay_dum - well_bot_dum)
                            w.append(lay_length)

            w = w / screen_length_dum





        #Now, let's grab simulations for the well



        sim_dum=gwhyd_sim.loc[gwhyd_sim['HYDROGRAPH ID'].isin(IDs_dum),['Date','HYDROGRAPH ID', 'LAYER','SIM']].reset_index(drop=True)

        #Let's transform to wide
        sim_dum_wide=sim_dum.pivot(index="Date",columns='LAYER',values="SIM")

        #Names for wide dataframe
        wide_names=[]

        for i in range(len(IDs_dum)):
            lay_dum=wells_dum.loc[wells_dum["HYDROGRAPH ID"]==IDs_dum[i],'IOUTHL'].values[0]
            wide_names.append("Layer_"+str(lay_dum))

        sim_dum_wide.columns = wide_names
        sim_dum_wide["Date"]=sim_dum_wide.index

        sim_dum_wide=sim_dum_wide[["Date"] + wide_names].reset_index(drop=True)
        if sim_dum.shape[0] > 0:

            #Let's calculate weighted average
            avg_w=sim_dum_wide.iloc[:,1]*0
            for i in range(len(IDs_dum)):
                avg_w=avg_w+(sim_dum_wide['Layer_'+str(i+1)]*w[i])
            sim_dum_wide["Avg_w"]=avg_w

            #Let's prepare dates to join dataframes

            # sim_dum_wide.loc[:,"Year_Month"]=pd.to_datetime(sim_dum_wide.Date.dt.strftime('%Y/%m'))
            sim_dum_wide.loc[:,"Year_Month"]=sim_dum_wide.Date.dt.strftime('%Y/%m')

            # gwl_dum.loc[:,"Year_Month"]=pd.to_datetime(gwl_dum.Date.dt.strftime('%Y/%m'))
            gwl_dum.loc[:,"Year_Month"]=gwl_dum.Date.dt.strftime('%Y/%m')

            all_wide=pd.merge(sim_dum_wide, gwl_dum[["Year_Month",'WSE']], on="Year_Month", how='left')

            #Let's export to csv
            all_wide.to_csv(os.path.join(dir_out,well+".csv"))

            #Let's plot observations

            ax = gwl_dum.plot(x='Date',y='WSE',marker='o',linestyle = 'None',title=well)
            #Let's plot the rest of the series
            for i in range(len(IDs_dum)):
                sim_dum_wide.plot(ax=ax, x='Date', y='Layer_'+str(i+1))

            #If there is more than one layer and less than nlay, we add weighted average
            if (len(IDs_dum)>1) and (len(IDs_dum)<nlay):
                sim_dum_wide.plot(ax=ax, x='Date', y='Avg_w')

            #obs_dum.plot(ax=ax, x='Date', y='SIM')
            #y_lb=int((gwl_dum.WSE.mean()-y_range/2)/5)*5
            #y_ub=y_lb+y_range
            y_lb=-75
            y_ub=75
            ax.set_ylim(y_lb,y_ub)
            #Let's set tickmarks
            axes=ax.axes
            year_0=sim_dates.Date.dt.year[0]
            year_f = sim_dates.Date.dt.year[1]
            xticks_dum=pd.date_range(start=sim_dates.Date[0], end=sim_dates.Date[1], freq='Y')
            xlabs_dum=xticks_dum.strftime('%Y')
            yticks_dum=list(range(-75,100,25))
            ax.axes.set_xticks(xticks_dum)
            ax.axes.set_yticks(yticks_dum)
            ax.axes.set_xticklabels(xlabs_dum)
            fig = ax.get_figure()
            fig.savefig(os.path.join(dir_out,well+".png"))
            fig.clear()

            # Let's remove rows with nas
            all_wide_dum = all_wide[~all_wide['WSE'].isna()]
            #Now, let's draw scatterplots for the layers
            for i in range(len(IDs_dum)):

                r2 = sklearn.metrics.r2_score(all_wide_dum['WSE'], all_wide_dum['Layer_'+str(i+1)])
                #axis limits
                lb=np.min(all_wide_dum[['WSE','Layer_'+str(i+1)]].min().values)
                ub=np.max(all_wide_dum[['WSE','Layer_'+str(i+1)]].max().values)

                #Let's turn into integers
                lb=(round(lb/5)-1)*5
                ub=(round(ub/5)+1)*5

                ax = all_wide_dum.plot.scatter(x='WSE', y='Layer_'+str(i+1), title=well+" Layer "+str(i+1))
                ax.axline((1, 1), slope=1, color='g')

                #Let's add text
                ax.text(ub - 5,
                        ub- 1,
                        "r2= " + str(round(r2, 2)))

                #Let's set axis limits
                ax.set_xlim(lb,ub)
                ax.set_ylim(lb, ub)
                fig = ax.get_figure()
                fig.savefig(os.path.join(dir_out, "OBS_vs_SIM_" + well +"_Layer_"+str(i+1)+ ".png"))
                fig.clear()

            #Now, we do the same for the average
            r2 = sklearn.metrics.r2_score(all_wide_dum['WSE'], all_wide_dum['Avg_w'])
            # axis limits
            lb = np.min(all_wide_dum[['WSE', 'Avg_w']].min().values)
            ub = np.max(all_wide_dum[['WSE', 'Avg_w']].max().values)

            # Let's turn into integers
            lb = (round(lb / 5) - 1) * 5
            ub = (round(ub / 5) + 1) * 5

            ax = all_wide_dum.plot.scatter(x='WSE', y='Avg_w', title=well + ' Avg_w')
            ax.axline((1, 1), slope=1, color='g')

            # Let's add text
            ax.text(ub - 5,
                    ub - 1,
                    "r2= " + str(round(r2, 2)))

            # Let's set axis limits
            ax.set_xlim(lb, ub)
            ax.set_ylim(lb, ub)
            fig = ax.get_figure()
            fig.savefig(os.path.join(dir_out, "OBS_vs_SIM_" + well + "_Avg_w.png"))
            fig.clear()



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

    return IWFM_in_CASGEM, IWFM_not_in_CASGEM, CASGEM_not_in_IWFM, CASGEM_outside_range, OBS, ranges

