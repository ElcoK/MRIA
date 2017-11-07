# -*- coding: utf-8 -*-
"""
This script will produce an uncertainty analysis around the results. This 
should improve the interpretation of the modelling outcomes

@author: Elco Koks

@date: Nov, 2017
"""

import pandas as pd
import itertools
from mria_py.core.model import MRIA_IO,MRIA_SUT
import numpy as np

class ua(object):

    def __init__(self, data):
        self.countries = data.countries
        self.total_countries = len(data.countries)
        self.sectors = data.sectors    
        self.data = data

   
    def run_IO(self,disruption = 1.1,disrupted_ctry= [],disrupted_sctr=[]):
        """
        Run an uncertainty analysis around the different weights between the 
        disaster imports and rationing for an IO modelling setup
        """
        
        Weights = np.arange(0, 2.25, 0.25)
        output_UA = pd.DataFrame(columns=['DisWeight','RatWeight','Loss'])

        for Weight1,Weight2 in itertools.combinations(Weights,2):

            '''Create model'''
            MRIA_RUN = MRIA_IO(self.data.name,self.data.countries,self.data.sectors,self.data.FD_cat)
            
            '''Define sets and alias'''
            # CREATE SETS
            MRIA_RUN.create_sets(FD_SET=self.data.FD_cat)
            
            # CREATE ALIAS
            MRIA_RUN.create_alias()
        
            ''' Define tables and parameters'''
            output = pd.DataFrame()
            MRIA_RUN.baseline_data(self.data,disruption,disrupted_ctry,disrupted_sctr)
            output['x_in'] = pd.Series(MRIA_RUN.X.get_values())
    
            MRIA_RUN.impact_data(self.data,disruption,disrupted_ctry,disrupted_sctr)

      
            MRIA_RUN.run_impactmodel(DisWeight=Weight1,RatWeight=Weight2)
            
            output['x_out'] = pd.Series(MRIA_RUN.X.get_values())
            output['loss'] = output['x_in'] - output['x_out']
          
            print('A DisWeight of '+str(Weight1)+' and a RatWeight of '+str(Weight2)+' gives a loss of '+str(sum(output['loss']))+ ' million  dollar')
            
            output_UA = output_UA.append({'DisWeight':Weight1,'RatWeight':Weight2,'Loss':sum(output['loss'])}, ignore_index=True)
            
        return output_UA

    def run_SUT(self,disruption = 1.1,disrupted_ctry= [],disrupted_sctr=[]):
        """
        Run an uncertainty analysis around the different weights between the 
        disaster imports and rationing for a SUT modelling setup
        """
        
        Weights = np.arange(0, 2.25, 0.25)
        output_UA = pd.DataFrame(columns=['DisWeight','RatWeight','Loss'])

        for Weight1,Weight2 in itertools.combinations(Weights,2):

            '''Create model'''
            MRIA_RUN = MRIA_SUT(self.data.name,self.data.countries,self.data.sectors,self.data.products,self.data.FD_cat)
            
            '''Define sets and alias'''
            # CREATE SETS
            MRIA_RUN.create_sets()
            
            # CREATE ALIAS
            MRIA_RUN.create_alias()
        
            ''' Define tables and parameters'''
            output = pd.DataFrame()
            MRIA_RUN.baseline_data(self.data,disruption,disrupted_ctry,disrupted_sctr) 
            output['x_in'] = pd.Series(MRIA_RUN.X.get_values())
    
            MRIA_RUN.impact_data(self.data,disruption,disrupted_ctry,disrupted_sctr)

      
            MRIA_RUN.run_impactmodel(DisWeight=Weight1,RatWeight=Weight2)
            
            output['x_out'] = pd.Series(MRIA_RUN.X.get_values())
            output['loss'] = output['x_in'] - output['x_out']
          
            print('A DisWeight of '+str(Weight1)+' and a RatWeight of '+str(Weight2)+' gives a loss of '+str(sum(output['loss']))+ ' million  dollar')
            
            output_UA = output_UA.append({'DisWeight':Weight1,'RatWeight':Weight2,'Loss':sum(output['loss'])}, ignore_index=True)
            
        return output_UA    