# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 13:52:00 2017

@author: cenv0574
"""

# Import
import pandas as pd 
import geopandas as gp
import numpy as np
import sys
import os

mria_path = r'F:\Dropbox\Oxford\MRIA\mria_py'  
if not mria_path in sys.path:
    sys.path.append(mria_path)

if __name__ == '__main__':

    _mriapath = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, _mriapath + '/../../')
    
    from mria_py.core.create_table import Table_SUT as Table
    from mria_py.core.base_model import MRIA_SUT as MRIA
    
    ''' Specify file path '''
    filepath = '..\..\input_data\The_Vale_SUT.xlsx'

    '''Specify which countries should be included in the subset'''

    list_countries = ['Elms','Hazel','Montagu','Fogwell','Riverside','Oatlands']


    '''Create data input'''
    DATA = Table('TheVale_SuT',filepath,2010,list_countries)
    DATA.prep_data()
    

    ''' Run uncertainty analysis'''
#    output = ua(DATA).run()

    '''Create model '''    
    MRIA_model = MRIA(DATA.name,DATA.countries,DATA.sectors,DATA.products)
    MRIA_model.create_sets(FD_SET=['FinalD'])
    MRIA_model.create_alias()


    '''Run model and create some output'''
    output = pd.DataFrame()
 
#    MRIA_model.run_basemodel()

    '''Specify disruption'''
    disruption = 0.9
    disrupted_ctry =  ['Elms']
    disrupted_sctr = ['Manu']

    MRIA_model.baseline_data(DATA,disruption,disrupted_ctry,disrupted_sctr) 

    output['x_in'] = pd.Series(MRIA_model.X.get_values())

#    MRIA_model.run_basemodel()

    MRIA_model.impact_data(DATA,disruption,disrupted_ctry,disrupted_sctr)
    MRIA_model.run_impactmodel(output=True)
  
    output['x_out'] = pd.Series(MRIA_model.X.get_values())
    output['loss'] = output['x_out'] - output['x_in']

    print(sum(output['loss']))

    '''And visualize it'''
    
    shape_TheVale = gp.read_file('..\\..\\input_data\\The_Vale.shp')
    reg_loss = pd.DataFrame(output[['loss','x_in']].groupby(level=0).sum())
    reg_loss['loss_rel'] = (reg_loss['loss']/reg_loss['x_in'])*100 
    reg_loss['Region'] = reg_loss.index
    
    reg_loss['loss'] = reg_loss['loss'].round()
    reg_loss['loss_rel'] = reg_loss['loss_rel'].astype((np.float16))

    reg_shap = pd.merge(shape_TheVale, reg_loss, on='Region', how='inner')
    reg_shap.plot(column='loss', cmap='OrRd', legend=True) 
