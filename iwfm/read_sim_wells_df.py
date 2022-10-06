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


def read_sim_wells_df(gw_file,sm_pywfm,crs=26910,
                      wells_flag="C       ID   HYDTYP   IOUTHL         X               Y         IOUTH        Name                      Comment",
                      nouth_flag="/ NOUTH",
                      end_wells_flag="C*******************************************************************************"
                      ):
    ''' read_sim_wells_df() - Read Groundwater.dat file and build a dictionary of
        groundwater hydrograph info and gwhyd_sim columns, and returns
        Pandas dataframe

    Parameters
    ----------
    gw_file : str
        IWFM Groundwater.dat file name
    crs: int
        EPSG number of reference system usde in the wells coordinates

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
    import geopandas

    #Let's import wells file
    lines = (open(gw_file).read().splitlines())

    #Let's find nouth variable
    lines_i = 0

    while lines[lines_i].find(nouth_flag) < 0:
        lines_i += 1
    lines_new = lines[0:lines_i]

    line_nouth=lines[lines_i].split()
    nouth=int(line_nouth[0])

    GWHYDOUTFL=lines[lines_i+2].split()[0]

    #Let's find where the wells section starts

    while lines[lines_i].find(wells_flag) < 0:
        lines_i += 1
    lines_i +=2

    #Number of layers
    nlay=sm_pywfm.get_n_layers()
    colnames=["Name", "HYDROGRAPH ID", "X", "Y", "IOUTHL", "Comment"]
    colnames.append("Top")

    for i in range(nlay):
        colnames.append("L"+str(i+1)+"_bot")

    #Let's create dataframe where we will store the wells
    wells_df=pd.DataFrame(columns=colnames)



    #let's loop and add lines
    while lines[lines_i].find(end_wells_flag) < 0:
        line_dum=lines[lines_i]
        line_dum_list=line_dum.split("\t")
        name_dum=line_dum_list[6]
        if name_dum.find("_L")>0:
                name_dum=name_dum[:name_dum.find("_L")]
        id_dum=line_dum_list[0]
        x_dum=float(line_dum_list[3])
        y_dum = float(line_dum_list[4])
        comment_dum=line_dum_list[8]
        IOUTHL_dum=line_dum_list[2]
        lith_dum=sm_pywfm.get_stratigraphy_atXYcoordinate(x_dum, y_dum, 3.2808)
        top_dum=lith_dum[0]
        dict_dum={"Name":[name_dum],
                  "HYDROGRAPH ID":[id_dum],
                  "X":[x_dum],
                  "Y":[y_dum],
                  "IOUTHL":[IOUTHL_dum],
                  "Comment":[comment_dum],
                  "Top":[lith_dum[0]]}

        for i in range(nlay):
            dict_dum["L"+str(i+1)+"_bot"]=[lith_dum[i+1]]

        wells_df_dum=pd.DataFrame(dict_dum)
        wells_df=wells_df.append(wells_df_dum,ignore_index=True)


        lines_i += 1


    wells_gdf = geopandas.GeoDataFrame(wells_df.copy(), geometry=geopandas.points_from_xy(wells_df.X, wells_df.Y,crs="EPSG:"+str(crs)))


    return wells_df, nouth, GWHYDOUTFL, wells_gdf
