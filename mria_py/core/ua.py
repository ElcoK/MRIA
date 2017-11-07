# -*- coding: utf-8 -*-
"""
This script will produce an uncertainty analysis around the results. This 
should improve the interpretation of the modelling outcomes

@author: Elco Koks

@date: Nov, 2017
"""

import pandas as pd
import itertools
from mria_py.core.create_table import Table
from mria_py.core.base_model import MRIA_IO as MRIA


class ua(object):

    def __init__(self, data):
        self.countries = data.countries
        self.total_countries = len(data.countries)
        self.sectors = data.sectors    
        self.data = data

   
    def run(self,disruption = 1.1,disrupted_ctry= [],disrupted_sctr=[]):
        
        Weights = [0,0.5,1,1.25,1.5,1.75,2,2.25,2.5]
        output_UA = pd.DataFrame(columns=['DisWeight','RatWeight','Loss'])

        for DisWeight,RatWeight in itertools.combinations(Weights,2):

            '''Create model'''
            MRIA_RUN = MRIA(self.data.name,self.data.countries,self.data.sectors)
            
            '''Define sets and alias'''
            # CREATE SETS
            MRIA_RUN.create_sets()
            
            # CREATE ALIAS
            MRIA_RUN.create_alias()
        
            ''' Define tables and parameters'''
            output = pd.DataFrame()
            MRIA_RUN.baseline_data(self.data,disruption,disrupted_ctry,disrupted_sctr)
#            MRIA_RUN.impact_data(self.data,disruption,disrupted_ctry,disrupted_sctr)
#            output['x_in'] = pd.Series(MRIA_RUN.X.get_values())
#        
#            MRIA_RUN.run_impactmodel(DisWeight=DisWeight,RatWeight=RatWeight)
#            
#            output['x_out'] = pd.Series(MRIA_RUN.X.get_values())
#            output['loss'] = output['x_in'] - output['x_out']
#          
#            print('A DisWeight of '+str(DisWeight)+' and a RatWeight of '+str(RatWeight)+' gives a loss of '+str(sum(output['loss']))+ ' dollar')
#            
#            output_UA = output_UA.append({'DisWeight':DisWeight,'RatWeight':RatWeight,'Loss':sum(output['loss'])}, ignore_index=True)
#    
#            del MRIA_RUN   
            
        return output_UA
                
if __name__ == '__main__':


    ''' Specify file path '''
    filepath = '..\..\input_data\The_Vale.xlsx'

    '''Specify which countries should be included in the subset'''

    list_countries = ['Elms','Hazel','Montagu','Fogwell','Riverside','Oatlands']


    '''Create data input'''
    DATA = Table('TheVale',filepath,2010,list_countries)
    DATA.prep_data()
    

    '''Create model '''    
    MRIA_model = MRIA(DATA.name,list_countries,DATA.sectors)
    MRIA_model.create_sets(FD_SET=['FinDem'])
    MRIA_model.create_alias()


    '''Run model and create some output'''
    output = pd.DataFrame()
 
#    MRIA_model.run_basemodel()

    '''Specify disruption'''
    disruption = 1.1
    disrupted_ctry =  ['Elms']
    disrupted_sctr = ['Manu']

    MRIA_model.baseline_data(DATA,disruption,disrupted_ctry,disrupted_sctr) 

    output['x_in'] = pd.Series(MRIA_model.X.get_values())

#    MRIA_model.run_basemodel()

    MRIA_model.impact_data(DATA,disruption,disrupted_ctry,disrupted_sctr)
    MRIA_model.run_impactmodel()
  
    output['x_out'] = pd.Series(MRIA_model.X.get_values())
    output['loss'] = output['x_out'] - output['x_in']
    
    MRIA_RUN = MRIA(ua(DATA).data.name,ua(DATA).data.countries,ua(DATA).data.sectors)
    
    MRIA_RUN.create_sets(FD_SET=['FinDem'])
    MRIA_RUN.create_alias()
    
    ua(DATA)

    
    MRIA_RUN.baseline_data(ua(DATA).data,disruption,disrupted_ctry,disrupted_sctr)
    MRIA_RUN.run_basemodel()