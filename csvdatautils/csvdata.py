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
from typing import List, Union

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
        the string 'none' (or any variation: 'None', 'NONE', etc.) which will be stored as None.

        Args:
            csvfile (str): the path to the ROSData CSV file
        """

        # Class Variables
        self._data = []
        self._fields = []

        # Read CSV file
        with open(csvfile, newline='') as f:
            csvreader = csv.reader(f, delimiter=',')
            for idx, row in enumerate(csvreader):
                if idx == 0:
                    self._fields = row
                else:
                    self._data.append(CSVDataRow(row, self._fields, mappings))
            f.close()       


    def field_exists(self, field : str) -> bool:
        """Checks to see if a field exists within this CSV data

        Args:
            field (str): the field

        Returns:
            bool: true if the field exists
        """

        if field in self._fields:
            return True
        return False
    
    def get_row(self, index: int) -> CSVDataRow:
        """Gets the CSVDataRow object for the provided index.

        Args:
            index (int): the index to retrieve

        Raises:
            IndexError: if the index does not exist.

        Returns:
            CSVDataRow: the returned CSVDataRow object for the passed index.
        """
        if index >= len(self):
            raise IndexError(f"Attempting to access an index ({index}) that does not exist.")
        return self._data[index]

    
    def get_data(self, indices: Union[int, List[int], List[float]]=None,
                 fields: Union[str, List[str]]=None) -> Union[float, str, List[Union[float, str]]]:
        """Gets the entire data for a specific index or field. Can also return the value for
        a specific field and index, or the set of values for a specific set of fields and indices.

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
            indices (int, str, list): the index or indices to be retrieved
            fields (optional, int or str): the field or fields to be retrieved

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

        if len(indices) != 0 and len(fields) != 0:
            retval = []
            for x in indices:
                if len(fields) == 1:
                    retval.append(getattr(self._data[x], fields[0]))
                else:
                    retval.append([getattr(self._data[x], y) for y in fields])
        elif len(indices) != 0:
            retval = [self._data[x] for x in indices]
        elif len(fields) != 0:
            retval = []
            for x in self._data:
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
        


    def __getitem__(self, index: int) -> CSVDataRow:
        """Can be used as a shorthand for the get_row method. 
        
        Examples:

            | # equivalent to csvrosdata_obj.get_data(indices=0)
            | csvrosdata_obj[0] 

            | # equivalent to csvrosdata_obj.get_data(fields='timestamp')
            | csvrosdata_obj['timestamp'] 

            | # equivalent to csvrosdata_obj.get_data(indices=0, fields='timestamp')
            | csvrosdata_obj[0, 'timestamp'] 
        """

        return self.get_row(index)


    def __len__(self) -> int:
        """returns the length of the data

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