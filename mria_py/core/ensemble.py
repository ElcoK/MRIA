# -*- coding: utf-8 -*-
"""
This script allows for running an ensemble of different multiregional models,
for the same subset of countries. This will improve the interpretation of 
the modelling outcomes.

@author: Elco Koks

@date: Nov, 2017
"""

class ensemble(object):    
    

    def __init__(self, *datasets):
        self.countries = data.countries
        self.total_countries = len(data.countries)
        self.sectors = data.sectors    

