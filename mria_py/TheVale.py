# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 13:52:00 2017

@author: cenv0574
"""

# Import
#from pyomo.environ import *
import os
from pyomo.environ import ConcreteModel,Set,SetOf,Param,Var,Constraint,Objective,minimize, ConstraintList
import pandas as pd 
import geopandas as gp
from base_model import MRIA
from create_table import Table
import numpy as np

curdir = os.getcwd()


if __name__ == '__main__':


    ''' Specify file path '''
    filepath = '..\input_data\The_Vale.xlsx'

    '''Specify which countries should be included in the subset'''

    list_countries = ['Elms','Hazel','Montagu','Fogwell','Riverside','Oatlands']

    '''Specify disruption'''
    disruption = 1.1
    disrupted_ctry =  ['Elms']
    disrupted_sctr = ['Manu']

    '''Create data input'''
    DATA = Table('TheVale',filepath,2010,list_countries)
    DATA.prep_data()

    '''Create model '''    
    MRIA_model = MRIA('TheVale',list_countries,DATA.sectors)
    MRIA_model.create_sets(FD_SET=['FinDem'])
    MRIA_model.create_alias()

    '''Run model and create some output'''
    output = pd.DataFrame()
    
    MRIA_model.baseline_data(DATA,disruption,disrupted_ctry,disrupted_sctr)    
    MRIA_model.impact_data(DATA,disruption,disrupted_ctry,disrupted_sctr)
    
    output['x_in'] = pd.Series(MRIA_model.X.get_values())
   
    MRIA_model.run_impactmodel()
  
    output['x_out'] = pd.Series(MRIA_model.X.get_values())
    output['loss'] = output['x_out'] - output['x_in']

    print(sum(output['loss']))

    '''And visualize it'''
    
    shape_TheVale = gp.read_file('..\\input_data\\The_Vale.shp')
    reg_loss = pd.DataFrame(output[['loss','x_in']].groupby(level=0).sum())
    reg_loss['loss_rel'] = (reg_loss['loss']/reg_loss['x_in'])*100 
    reg_loss['Region'] = reg_loss.index
    
    reg_loss['loss'] = reg_loss['loss'].round()
    reg_loss['loss_rel'] = reg_loss['loss_rel'].astype((np.float16))

    reg_shap = pd.merge(shape_TheVale, reg_loss, on='Region', how='inner')
    reg_shap.plot(column='loss', cmap='OrRd', legend=True) 
           


