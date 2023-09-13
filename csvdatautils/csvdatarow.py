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

from typing import Any, Dict, List, Tuple

###############
### CLASSES ###
###############



class CSVDataRow():
    """A helper class to store a single row of data contained within a CSV, or CSV like, file.
    """

    def __init__(self, data: list, fields: list, mappings: dict={}) -> None:
        """Initialises a CSVDataRow object where the fields argument defines the set of
        class attributes. The mappings argument allows getting of an attribute via multiple names.
        
        Numeric data will be stored as floats, all other data will be stored as strings except for
        the strings '' and 'none' (or any variation: 'NONE', etc.) which will be stored as None.

        Args:
            data (list): the values for the provided fields
            fields (list): the names for each field provided within the data
            mappings (bool, optional): the field/attribute mappings. Allows the retrieval of the same
              data value via mutliple names. Format is {'mapped_name': '<field_name>'}. Defaults to {}.

        Raises:
            ValueError: if the length of the fields and data arguments are not equal.
        """

        self._fields = fields
        self._mappings = mappings
        
        # Check fields and data are same length
        if len(fields) != len(data):
            raise ValueError("The number of fields must be equal to size of the data")

        # Attempt to convert data to float
        for idx in range(len(data)):
            val = data[idx]
            try:
                # attempt to convert to float
                val = float(val)
            except ValueError:
                if val.lower() == 'none' or val == '':
                    # if was the string none, then convert to None type
                    val = None
            
            # set val
            data[idx] = val

        # Set class variables (attributes)
        for idx, field in enumerate(fields):
            setattr(self, field, data[idx])


    @property
    def fields(self) -> List:
        return self._fields

    @property
    def mappings(self) -> Dict:
        return self._mappings 
    
    
    def data(self) -> Dict:
        return {x: getattr(self, x) for x in self._fields}

    def __getattr__(self, __name: str) -> Any:
        return getattr(self, self._mappings[__name])
    

    def __getitem__(self, item: int) -> Tuple:
        mappings = [x for x,y in self._mappings.items() if y == self._fields[item]]
        return (self._fields[item], getattr(self, self._fields[item]), mappings)
    

    def __len__(self) -> int:
        return len(self._fields)

    def __str__(self):
        return ", ".join([f"{getattr(self, x)} ({x})" for x in self._fields])
            



########################
### PUBLIC FUNCTIONS ###
########################



#########################
### PRIVATE FUNCTIONS ###
#########################