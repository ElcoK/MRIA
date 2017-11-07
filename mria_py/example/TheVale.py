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
    
    from mria_py.core.table import io_basic
    from mria_py.core.model import MRIA_IO as MRIA
    from mria_py.core.visualize import visualize
    from mria_py.core.basics import basic_IO
    
    ''' Specify file path '''
    filepath = '..\..\input_data\The_Vale.xlsx'

    '''Specify which countries should be included in the subset'''

    list_countries = ['Elms','Hazel','Montagu','Fogwell','Riverside','Oatlands']


    '''Create data input'''
    DATA = io_basic('TheVale',filepath,2010,list_countries)
    DATA.prep_data()
    
    '''Look at the data to see if it makes sense'''
    visualize(DATA).heatmap()
    
    '''Check if table is balanced'''
    basic_IO(DATA).check_table()
    
    '''Create model '''    
    MRIA_model = MRIA(DATA.name,list_countries,DATA.sectors,DATA.FD_cat)
    MRIA_model.create_sets(FD_SET=['FinDem'])
    MRIA_model.create_alias()


    '''Run model and create some output'''
    output = pd.DataFrame()
 
    '''Specify disruption'''
    disruption = 1.1
    disrupted_ctry =  ['Elms','Hazel']
    disrupted_sctr = ['Manu']

    MRIA_model.baseline_data(DATA,disruption,disrupted_ctry,disrupted_sctr) 

    output['x_in'] = pd.Series(MRIA_model.X.get_values())

    MRIA_model.impact_data(DATA,disruption,disrupted_ctry,disrupted_sctr)
    MRIA_model.run_impactmodel(DisWeight=1.75,RatWeight=2)
  
    output['x_out'] = pd.Series(MRIA_model.X.get_values())
    output['loss'] = output['x_out'] - output['x_in']

    print('A DisImp of '+str(sum(pd.Series(MRIA_model.DisImp.get_values())))+' and a Rat of '+str(sum(pd.Series(MRIA_model.Rat.get_values())))+' gives a loss of '+str(sum(output['loss']))+ ' dollar')

    '''And visualize it'''
    
    shape_TheVale = gp.read_file('..\\..\\input_data\\The_Vale.shp')
    reg_loss = pd.DataFrame(output[['loss','x_in']].groupby(level=0).sum())
    reg_loss['loss_rel'] = (reg_loss['loss']/reg_loss['x_in'])*100 
    reg_loss['Region'] = reg_loss.index
    
    reg_loss['loss'] = reg_loss['loss'].round()
    reg_loss['loss_rel'] = reg_loss['loss_rel'].astype((np.float16))

    reg_shap = pd.merge(shape_TheVale, reg_loss, on='Region', how='inner')
    reg_shap.plot(column='loss', cmap='OrRd', legend=True) 
