# iwfm_model.py
# Python class for IWFM model information
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

import iwfm as iwfm
import re
import os
from shapely.geometry import Point, Polygon


class iwfm_model:
    def __init__(self, pre_fpath, sim_file, verbose=False):
        self.mtype = 'IWFM'
        fpath_line = pre_fpath.split('\\')  # Preprocessor file path to list
        self.pre_file = fpath_line.pop(
            len(fpath_line) - 1
        )  # pop preprocessor file name from list
        #self.pre_folder = Path(
        #    '/'.join(fpath_line)
        self.pre_folder='//'.join(fpath_line)
        #)  # put back together as Path object for all OSs
        
        self.sim_file = sim_file  # simulation file name

        if verbose:
            print('\n  Reading IWFM Files')

        # -- read preprocessor main file
        currfile = os.path.join(self.pre_folder,self.pre_file)
        if verbose:
            print(f'    IWFM pre-processor file: \t{currfile}')
        self.read_preproc(currfile)

        # -- read preprocessor node file
        currfile = os.path.join(self.pre_folder,self.pre_files_dict['node_file'])
        if verbose:
            print(f'    IWFM node file:          \t{currfile}')
        self.read_nodes(currfile)

        # -- read preprocessor element file
        currfile = os.path.join(self.pre_folder,self.pre_files_dict['elem_file'])
        if verbose:
            print(f'    IWFM elements file:      \t{currfile}')
        self.read_elements(currfile)

        # -- read preprocessor stratigraphy file
        currfile = os.path.join(self.pre_folder,self.pre_files_dict['strat_file'])
        if verbose:
            print(f'    IWFM stratigraphy file:  \t{currfile}')
        self.read_strat(currfile)

        # -- read simulation main file 
        currfile = self.sim_file
        if verbose:
            print(f'    IWFM simulation main file:\t{currfile}')
        self.read_sim(currfile)
        return


    # -- functions to return information
    def nlayers(self):
        return self.nlayers

    def lse(self):
        return self.lse

    def aquifer_thickness(self):
        return self.aquifer_thick

    def aquifer_top(self):
        return self.aquifer_top

    def aquifer_bottom(self):
        return self.aquifer_bottom

    def aquitard_thickness(self):
        return self.aquitard_thick

    def aquitard_top(self):
        return self.aquitard_top

    def aquitard_bottom(self):
        return self.aquitard_bottom

    # -- the functions that do the work 
    def read_preproc(self, pre_file):
        ''' read_prepcoc() - Read an IWFM Preprocessor main input file, and 
            return a list of the files called and some settings.'''
        # -- read the preprocessor file into array file_lines
        pre_lines = open(pre_file).read().splitlines()  # open and read input file

        line_index = iwfm.skip_ahead(0, pre_lines, 3)  # skip comments

        # -- read input file names and create a dictionary ------------------
        self.pre_files_dict = {}
        self.pre_files_dict['preout'] = pre_lines[line_index].split()[0] 

        line_index = iwfm.skip_ahead(line_index + 1, pre_lines, 0)  
        self.pre_files_dict['elem_file'] = pre_lines[line_index].split()[0] 

        line_index = iwfm.skip_ahead(line_index + 1, pre_lines, 0)  
        self.pre_files_dict['node_file'] = pre_lines[line_index].split()[0]  

        line_index = iwfm.skip_ahead(line_index + 1, pre_lines, 0)  
        self.pre_files_dict['strat_file'] = pre_lines[line_index].split()[0] 

        line_index = iwfm.skip_ahead(line_index + 1, pre_lines, 0) 
        self.pre_files_dict['stream_file'] = pre_lines[line_index].split()[0] 

        line_index = iwfm.skip_ahead(line_index + 1, pre_lines, 0)  
        lake_file = pre_lines[line_index].split()[0]  
        if lake_file[0] == '/':
            lake_file = ''
        self.pre_files_dict['lake_file'] = lake_file
        return


    def read_sim(self, sim_file):
        ''' read_sim() - Read an IWFM Simulation main input file, and return
            a dictionary with the files called and some settings.'''

        sim_lines = open(sim_file).read().splitlines()  # open and read input file

        line_index = iwfm.skip_ahead(0, sim_lines, 3)  # skip comments

        # -- read input file names and create a dictionary 
        self.sim_files_dict = {}
        preout = iwfm.get_path(sim_lines[line_index].split()[0])  
        self.sim_files_dict['preout'] = preout

        line_index = iwfm.skip_ahead(line_index + 1, sim_lines, 0)
        gw_file = iwfm.get_path(sim_lines[line_index].split()[0]) 
        self.sim_files_dict['gw'] = gw_file

        line_index = iwfm.skip_ahead(line_index + 1, sim_lines, 0)
        stream_file = iwfm.get_path(sim_lines[line_index].split()[0])  
        self.sim_files_dict['stream'] = stream_file

        line_index = iwfm.skip_ahead(line_index + 1, sim_lines, 0)  
        temp = sim_lines[line_index].split()[0]  
        if temp[0] == '/':
            lake_file = ''
        else:
            lake_file = iwfm.get_path(temp)  
        self.sim_files_dict['lake'] = lake_file

        line_index = iwfm.skip_ahead(line_index + 1, sim_lines, 0)  
        rz_file = iwfm.get_path(sim_lines[line_index].split()[0])  
        self.sim_files_dict['rootzone'] = rz_file

        line_index = iwfm.skip_ahead(line_index + 1, sim_lines, 0) 
        sw_file = iwfm.get_path(sim_lines[line_index].split()[0])
        self.sim_files_dict['smallwatershed'] = sw_file

        line_index = iwfm.skip_ahead(line_index + 1, sim_lines, 0)  
        us_file = iwfm.get_path(sim_lines[line_index].split()[0])
        self.sim_files_dict['unsat'] = us_file

        line_index = iwfm.skip_ahead(line_index + 1, sim_lines, 0) 
        if_file = iwfm.get_path(sim_lines[line_index].split()[0])
        self.sim_files_dict['irrfrac'] = if_file

        line_index = iwfm.skip_ahead(line_index + 1, sim_lines, 0)  
        sa_file = iwfm.get_path(sim_lines[line_index].split()[0])
        self.sim_files_dict['supplyadj'] = sa_file

        line_index = iwfm.skip_ahead(line_index + 1, sim_lines, 0)  
        pc_file = sim_lines[line_index].split()[0] 
        self.sim_files_dict['precip'] = pc_file

        line_index = iwfm.skip_ahead(line_index + 1, sim_lines, 0)  
        et_file = iwfm.get_path(sim_lines[line_index].split()[0]) 
        self.sim_files_dict['et'] = et_file

        # -- starting date
        line_index = iwfm.skip_ahead(line_index + 1, sim_lines, 0)  
        start = sim_lines[line_index].split()[0]  
        self.sim_files_dict['start'] = start

        # -- time step
        line_index = iwfm.skip_ahead(line_index + 1, sim_lines, 1)  
        step = sim_lines[line_index].split()[0]  
        self.sim_files_dict['step'] = step

        # -- endng date
        line_index = iwfm.skip_ahead(line_index + 1, sim_lines, 0)  
        end = sim_lines[line_index].split()[0]  
        self.sim_files_dict['end'] = end
        return


    def read_nodes(self, node_file):
        ''' read_nodes() - Read an IWFM Node file, and return a list of the 
            nodes and their coordinates.'''

        # -- read the Node file into array file_lines
        node_lines = open(node_file).read().splitlines()  

        line_index = 0  # start at the top
        line_index = iwfm.skip_ahead(line_index, node_lines, 0)  # skip comments

        self.inodes = int(re.findall('\d+', node_lines[line_index])[0]) 

        line_index = iwfm.skip_ahead(line_index + 1, node_lines, 0)  # skip comments

        factor = float(node_lines[line_index].split()[0])  # read factor

        line_index = iwfm.skip_ahead(line_index + 1, node_lines, 0)  # skip comments

        self.d_nodes = {}  # initialize nodal info dictionary
        self.d_nodexy = {}  # initialize elemental info dictionary
        for i in range(0, self.inodes):  # read nodes information
            l = node_lines[line_index + i].split()  # get next line
            inode = int(l.pop(0))  # node number
            self.d_nodes[i] = inode
            coords = [float(s) * factor for s in l]
            self.d_nodexy[inode] = coords
        return


    def read_elements(self, elem_file):
        ''' read_elements() - Read an IWFM Element file, and return a list of 
            the nodes making up each element.'''
        # -- read the Element file into array file_lines
        elem_lines = open(elem_file).read().splitlines()  # open and read input file

        line_index = 0  
        line_index = iwfm.skip_ahead(line_index, elem_lines, 0)  

        self.elements = int(re.findall('\d+', elem_lines[line_index])[0]) 

        line_index = iwfm.skip_ahead(line_index + 1, elem_lines, 0)  

        subregions = int(re.findall('\d+', elem_lines[line_index])[0])

        line_index = iwfm.skip_ahead(line_index + 1, elem_lines, 0)  
        line_index = iwfm.skip_ahead(line_index + 1, elem_lines, subregions - 1)

        self.e_nos = []  # initialize list of elem nos
        self.d_elem_nodes = {}  # initialize list of elem nodes
        self.d_elem_sub = {}  # initialize list of elem subregions
        for i in range(0, self.elements):  # read element information
            l = elem_lines[line_index + i].split()  # get the next line
            this_elem = int(l.pop(0))  # element no of this element
            self.e_nos.append(this_elem)  # add element no of this element
            nodes = [int(s) for s in l]
            self.d_elem_sub[this_elem] = nodes.pop(4)  # subregion of this element
            if nodes[3] == 0:
                nodes.pop(3)  # remove empty node on triangles
            self.d_elem_nodes[this_elem] = nodes  # nodes of this element
        self.elems2poly()  # build polygons
        return


    def read_chars(self, char_file, elem_nodes):
        ''' read_chars() - Read an IWFM Element Characteristics file and return
            a list of characteristics for each element.'''

        char_lines = open(char_file).read().splitlines()  # open and read input file

        char_index = 0  # start at the top
        char_index = iwfm.skip_ahead(char_index, char_lines, 0)  # skip comments
        self.elem_char = []
        for i in range(0, len(elem_nodes)):
            l = char_lines[char_index + i].split()
            this_elem = int(l.pop(0))
            chars = []
            chars.append(int(l.pop(0)))  # rain station
            chars.append(float(l.pop(0)))  # rain factor
            chars.append(int(l.pop(0)))  # drainage
            chars.append(int(l.pop(0)))  # subregion
            temp = int(l.pop(0))  # don't use
            chars.append(float(l.pop(0)))  # soil type
            self.elem_char.append(chars)
        return


    def read_lake_pre(self, lake_file):
        ''' read_lake() - Read an IWFM Lake file and return (a) a list of 
            elements and (b) a list of properties for each lake.'''
        lake_lines = open(lake_file).read().splitlines()  # open and read input file
        lake_index = 0  # start at the top
        lake_index = iwfm.skip_ahead(lake_index, lake_lines, 0)  # skip comments
        self.nlakes = int(lake_lines[lake_index].split()[0])
        self.lakes = []
        self.lake_elems = []
        for i in range(0, self.nlakes):
            lake_index = iwfm.skip_ahead(lake_index + 1, lake_lines, 0)  # skip comments
            l = lake_lines[lake_index].split()  # read first line of lake description
            lake_id = int(l.pop(0))
            max_elev = float(l.pop(0))
            next = int(l.pop(0))
            nelem = int(l.pop(0))
            self.lakes.append([lake_id, max_elev, next, nelem])
            for j in range(0, nelem):
                e = []
                if j > 0:  # need to read next line
                    lake_index = iwfm.skip_ahead(lake_index + 1, lake_lines, 0)
                    l = lake_lines[lake_index].split()  # get next line
                e.append(lake_id)  # lake number
                e.append(int(l[0]))  # element number
                self.lake_elems.append(e)
        return


    def read_streams_pre(self, stream_file):
        ''' read_streams() - Read an IWFM Stream Geometry file and compile
            a list of stream reaches and (b) a dictionary of stream nodes,
            and return the number of stream nodes.'''
        stream_lines = open(stream_file).read().splitlines()  # open and read input file

        stream_index = 0  # start at the top
        stream_index = iwfm.skip_ahead(stream_index, stream_lines, 0)
        self.nreach = int(stream_lines[stream_index].split()[0])  # no reaches

        stream_index += 1
        self.n_rating = int(stream_lines[stream_index].split()[0])  

        self.sreach_list = []
        snodes_list = []
        nsnodes = 0
        for i in range(0, self.nreach):  # cycle through stream reaches
            # read reach information
            stream_index = iwfm.skip_ahead(stream_index + 1, stream_lines, 0)
            l = stream_lines[stream_index].split()
            # streams package version 4.2
            reach = int(l.pop(0))
            snodes = int(l.pop(0))

            # ** FUTURE ** modify to work with all versions of stream package
            # streams package version 5
            # upper = int(l.pop(0))
            # lower = int(l.pop(0))
            # snodes = lower - upper + 1

            oflow = int(l.pop(0))
            # read stream node information
            for j in range(0, snodes):
                stream_index = iwfm.skip_ahead(stream_index, stream_lines, 1)
                l = stream_lines[stream_index].split()
                t = [int(l[0]), int(l[1]), reach]  #  snode, GW Node, reach
                snodes_list.append(t)
                if j == 0:
                    upper = int(l[0])
                else:
                    lower = int(l[0])
            self.sreach_list.append([reach, upper, lower, oflow])

        stream_index = iwfm.skip_ahead(stream_index + 1, stream_lines, 3) 
        selev = []
        for i in range(0, len(snodes_list)):  
            l = stream_lines[stream_index].split()
            selev.append(float(l[1]))
            stream_index = stream_index + self.n_rating
            if i < len(snodes_list) - 1:  # stop at end
                stream_index = iwfm.skip_ahead(stream_index, stream_lines, 0)

        # put stream node info into a dictionary
        self.stnodes_dict = {}
        for i in range(0, len(snodes_list)):
            j = 0
            while snodes_list[j][0] != i + 1:  # find info for i in snodes list
                j += 1
            key, values = i + 1, [
                snodes_list[j][1],
                snodes_list[j][2],
                selev[i],
            ]  # key = snode, values = GW Node, Reach, Bottom
            self.stnodes_dict[key] = values
        return len(snodes_list)


    def read_strat(self, strat_file):

        strat_lines = open(strat_file).read().splitlines()  # open and read input file

        line_index = 0  # start at the top
        line_index = iwfm.skip_ahead(line_index, strat_lines, 0)  # skip comments
        layers = int(re.findall('\d+', strat_lines[line_index])[0])  # read no. layers

        line_index = iwfm.skip_ahead(line_index + 1, strat_lines, 0)  # skip comments
        factor = float(re.findall('\d+', strat_lines[line_index])[0])  # read factor

        line_index = iwfm.skip_ahead(line_index + 1, strat_lines, 0)  # skip comments
        self.strat = []  # initialize list
        for i in range(0, len(self.d_nodes)):
            l = strat_lines[line_index + i].split()
            s = []  # initialize accumulator
            s.append(int(l.pop(0)))  # node no
            for j in range(0, len(l)):
                s.append(factor * float(l.pop(0)))  # lse, etc as floats
            self.strat.append(s)

        self.nlayers = int((len(self.strat[0]) - 1) / 2)
        self.elevation = [i[0] for i in self.strat]

        self.d_nodeelev = {}
        for i in range(0, len(self.strat)):  # cycle through stratigraphy of each node
            l = self.strat[i]

            this_node = l.pop(0)
            lse = l.pop(0)

            depth = 0
            n_strat = []
            n_strat.append(lse)
            for j in range(0, self.nlayers):  # cycle through layers for each node
                t = l.pop(0)  # thickness of aquitard
                depth += t  # add to total depth
                n_strat.append(lse - depth)  # bottom of aquitard/top of aquifer
                a = l.pop(0)  # thickness of aquifer
                depth += a  # add to total depth
                n_strat.append(lse - depth)  # bottom of aquifer/top of next aqiutard
            self.d_nodeelev[this_node] = n_strat
        return


    def elems2poly(self):
        ''' elem_poly() - Compile a dictionary of model elements as shapely 
            polygons'''

        self.d_elem_polys = {}
        for key in self.d_elem_nodes:  # for each element ...
            elem = key
            nodes = self.d_elem_nodes[key]

            coords = []
            for node in nodes:  # for each node in the element ...
                # tuple of (x,y) coordinates
                coords.append(Point(self.d_nodexy[node][0], self.d_nodexy[node][1]))  
            # close the polygon
            coords.append(Point(self.d_nodexy[nodes[0]][0], self.d_nodexy[nodes[0]][1]))

            new_poly = Polygon([[p.x, p.y] for p in coords])
            self.d_elem_polys[elem] = new_poly  # list of coords for all elements
        return


    def point_in_elem(self, x, y):
        ''' point_in_elem() - Return the element number if the point (x,y) is 
            in an element, 0 otherwise'''
        p = Point(x, y)
        for key in self.d_elem_polys:  # for each element ...
            elem = key
            if p.within(self.d_elem_polys[elem]):
                return elem
        return 0

    def elem_coords(self):
        ''' elem_coords() - Return a list of coordinates of an element 
            [[x0,y0],[x1,y1],[x2,y2]<,...>]'''
        polys = []
        for i in range(0, len(self.elem_nodes)):  # for each element ...
            coords = []
            # for each node in the element ...
            for j in range(0, len(self.elem_nodes[i])):  
                coords.append(
                    (
                        self.node_coords[self.elem_nodes[i][j] - 1][0],
                        self.node_coords[self.elem_nodes[i][j] - 1][1],
                    )
                )
            coords.append(
                (
                    self.node_coords[self.elem_nodes[i][0] - 1][0],
                    self.node_coords[self.elem_nodes[i][0] - 1][1],
                )
            )  # close the polygon
            polys.append(coords)
        return polys
