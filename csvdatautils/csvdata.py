#!/usr/bin/env python

##################################################################################
# MIT License                                                                    #
#                                                                                #
# Copyright (c) 2022 James Mount                                                 #
#                                                                                #
# Permission is hereby granted, free of charge, to any person obtaining a copy   #
# of this software and associated documentation files (the "Software"), to deal  #
# in the Software without restriction, including without limitation the rights   #
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell      #
# copies of the Software, and to permit persons to whom the Software is          #
# furnished to do so, subject to the following conditions:                       #
#                                                                                #
# The above copyright notice and this permission notice shall be included in all #
# copies or substantial portions of the Software.                                #
#                                                                                #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR     #
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,       #
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE    #
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER         #
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,  #
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE  #
# SOFTWARE.                                                                      #
##################################################################################

###############
### MODULES ###
###############

import csv
import pathlib
from typing import Dict, List, Union

from csvdatautils.csvdatarow import *

###############
### CLASSES ###
###############


class CSVData():
    """A utility class to provide easy accessibility to data stored within CSV, or CSV-like, files.
    """

    def __init__(self, csvfile: str, mappings: dict={}) -> None:
        """Initialises a CSVData object. The CSV file should contain headers in the first row.
        All other rows are considered data. The headers within the CSV file will become the set
        of accessible fields.
        
        Numeric data will be stored as floats, all other data will be stored as strings except for
        the strings '' and 'none' (or any variation: 'NONE', etc.) which will be stored as None.

        Args:
            csvfile (str): the path to the ROSData CSV file
            mappings (bool, optional): the field/attribute mappings. Allows the retrieval of the same
              data value via mutliple names. Format is {'mapped_name': '<field_name>'}. Defaults to {}.
        """

        # Class Variables
        self._data = []
        self._fields = []
        self._mappings = mappings
        self._chunk = None

        # Read CSV file
        with open(csvfile, newline='') as f:
            csvreader = csv.reader(f, delimiter=',')
            for idx, row in enumerate(csvreader):
                if idx == 0:
                    self._fields = row
                else:
                    self._data.append(CSVDataRow(row, self._fields, mappings))
            f.close()

        # Reset chunk
        self.set_chunk(reset=True)     


    @property
    def fields(self) -> List[str]:
        """Gets the set of fields contained within the CSV data.

        Returns:
            List[str]: the list of fields.
        """
        return self._fields

    @property
    def mappings(self) -> Dict:
        """Gets the current mappings applied to the CSV data fields.

        Returns:
            Dict: the set of mappings.
        """
        return self._mappings  
    
    @property
    def chunk(self) -> List[CSVDataRow]:
        """Gets the current chunk.

        Returns:
            List[CSVDataRow]: gets the current chunk.
        """
        return self._chunk

    
    def set_chunk(self, start: int=0, stop: int=-1, step: int=1,
              reset: bool=False, operate_on_chunk: bool=False) -> None:
        """Set to perform operations on a chunk within the data.

        Args:
            start (int, optional): The start index to set for the chunk. Defaults to 0.
            stop (int, optional): The stop index to set for the chunk. Defaults to -1.
            step (int, optional): The step value to use. Defaults to 1.
            reset (bool, optional): Set to true to reset the chunk back to the full dataset. Defaults to False.
            operate_on_chunk (bool, optional): perform the operation on current chunk. Defaults to False.
        """

        # Reset if required
        if reset:
            self._chunk = self._data
        
        # Operating on current chunk or complete data
        data = self._data
        if operate_on_chunk:
            data = self._chunk

        # Set chunk
        self._chunk = data[start:stop:step]


    def has_field(self, field : str) -> bool:
        """Checks to see if a field exists within the CSV data

        Args:
            field (str): the field

        Returns:
            bool: true if the field exists
        """

        if field in self._fields:
            return True
        return False
    
    
    def get_row(self, item: Union[int,slice],
                operate_on_chunk: bool=False) -> Union[CSVDataRow, List[CSVDataRow]]:
        """Gets a specific index, or slice, from the data.

        Args:
            item (Union[int,slice]): the index or slice to return
            operate_on_chunk (bool, optional): perform the operation on current chunk. Defaults to False.

        Returns:
            Union[CSVDataRow, List[CSVDataRow]]: the returned CSVDataRow object or list of CSVDataRow objects
        """
                
        # Operating on current chunk or complete data
        data = self._data
        if operate_on_chunk:
            data = self._chunk

        return data[item]

    
    def get_subset(self, indices: Union[int, List]=None,
                 fields: Union[str, List]=None, operate_on_chunk: bool=False) -> Any:
        """Gets a subset of the data. The subset can be a desired set of row(s) and/or field(s).

        Examples:
            
            | # return data for index 0
            | data = csvrosdata_obj.get_data(0)   
            
            | # return all pos_x data
            | data = csvrosdata_obj.get_data('pos_x') 
            
            | # return all fields for multiple indices
            | data = csvrosdata_obj.get_data([0, 2])  

            | # return all data for a set of fields
            | data = csvrosdata_obj.get_data(['pos_x', 'pos_z'])  
            
            | # return multiple fields for a specified index or a set of indices
            | data = csvrosdata_obj.get_data(0, ['pos_x', 'pos_z']) 
            | data = csvrosdata_obj.get_data([0, 2], ['pos_x', 'pos_z'])  

        Args:
            indices (int, str, list): the index(s) to be retrieved
            fields (optional, int or str): the field(s) to be retrieved
            operate_on_chunk (bool, optional): perform the operation on current chunk. Defaults to False.

        Raises:
            ValueError: if too many arguments are provided

        Returns:
            variable: either the data (list) for a given index, the value for a given index/field or the data (list) for a field across all indices.
            
        """

        # if both indices and fields args are none
        # return entire data list

        # Argument check and conversion to correct format
        if indices is None:
            indices = []
        elif isinstance(indices, (int, float)):
            indices = [int(indices)] # change to int and convert to list
        elif isinstance(indices, list) and all(isinstance(x, (int, float)) for x in indices):
            indices = [int(x) for x in indices]
        else:
            raise ValueError("The indices argument must be a integer, float or list of integers or floats.")

        if fields is None:
            fields = []
        elif isinstance(fields, str):
            fields = [fields]
        elif isinstance(fields, list) and all(isinstance(x, str) for x in fields):
            pass # don't need to do anything
        else:
            raise ValueError("The fields argument must be a string, or list of strings.")

        # Operating on data or chunk
        data = self._data
        if operate_on_chunk:
            data = self._chunk

        # Get values
        if len(indices) != 0 and len(fields) != 0:
            retval = []
            for x in indices:
                if len(fields) == 1:
                    retval.append(getattr(data[x], fields[0]))
                else:
                    retval.append([getattr(data[x], y) for y in fields])
        elif len(indices) != 0:
            retval = [data[x] for x in indices]
        elif len(fields) != 0:
            retval = []
            for x in data:
                if len(fields) == 1:
                    retval.append(getattr(x, fields[0]))
                else:
                    retval.append([getattr(x, y) for y in fields])

        # only return the element if single item in list
        if len(retval) == 1:
            return retval[0]
        return retval
    

    def sort(self, field: str, reverse: bool=False) -> None:
        """Sorts the data given a field name.

        Args:
            field (str): the field to use to sort the data.
            reverse (bool, optional): Set to true to reverse the order. Defaults to True.
        """
        self._data.sort(key=lambda x: getattr(x, field), reverse=reverse)


    def save(self, fp: pathlib.Path, operate_on_chunk: bool = False) -> None:
        """Save the CSVData to a CSV file.

        Args:
            fp (pathlib.Path): the location to save the file.
            operate_on_chunk (bool, optional): perform the operation on current chunk. Defaults to False.
        """

        # Operating on current chunk or complete data
        data = self._data
        if operate_on_chunk:
            data = self._chunk

        # Open csv file, write header, than data
        with open(str(fp), 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self._fields)
            writer.writeheader()
            writer.writerows([x.data() for x in data])


    def __getitem__(self, item: Union[int,slice]) -> Union[CSVDataRow, List[CSVDataRow]]:
        """Gets a specific index, or slice, from the data. Operates on the entire data only,
        not on the current chunk (if set). Use the 'get_row' function if you wish to operate
        on the current chunk.

        Args:
            item (Union[int,slice]): the index or slice to return

        Returns:
            Union[CSVDataRow, List[CSVDataRow]]: the returned CSVDataRow object or list of CSVDataRow objects
        """
        
        return self.get_row(item, operate_on_chunk=False)


    def __len__(self) -> int:
        """returns the length of the data. Operates on the entire data only,
        not on the current chunk (if set).

        Returns:
            int: the length of the data
        """

        return len(self._data)


########################
### PUBLIC FUNCTIONS ###
########################



#########################
### PRIVATE FUNCTIONS ###
#########################