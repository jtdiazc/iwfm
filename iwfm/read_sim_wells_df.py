# read_sim_wells.py
# Read observation well information from IWFM Groundater.dat file
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


def read_sim_wells_df(gw_file):
    ''' read_sim_wellsdf() - Read Groundwater.dat file and build a dictionary of
        groundwater hydrograph info and gwhyd_sim columns, and returns
        Pandas dataframe

    Parameters
    ----------
    gw_file : str
        IWFM Groundwater.dat file name

    Returns
    -------
    well_dict : dictionary
        wells_df = Pandas dataframe with well information (name, ID
        x, y, model layer, well name)
        nouth= Total number of groundwater hydrographs to be printed
        GWHYDOUTFL= Filename for groundwater hydrograph output

    
    '''
    import iwfm as iwfm
    import pandas as pd
    well_dict, well_list, nouth, GWHYDOUTFL = iwfm.read_sim_wells(gw_file)
    # Let's create a pandas dataframe with the dictionary
    wells_df = pd.DataFrame.from_dict(well_dict, orient='index')
    wells_df = wells_df.reset_index()

    # Rename columns
    wells_df.columns = (["Name", "ID", "X", "Y", "IOUTHL", "State_Name"])


    return wells_df, nouth,GWHYDOUTFL
