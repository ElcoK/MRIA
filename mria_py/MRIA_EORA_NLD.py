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
from EORA_MRIA import MRIA
from EORA_TABLE import Table
import numpy as np

curdir = os.getcwd()


if __name__ == '__main__':

    ''' Specify current working directory'''
    curdir = os.getcwd()

    '''Specify which countries should be included in the subset'''
    list_countries = ['NLD','BEL','GBR','DEU']


    '''Specify disruption'''
    disruption = 1.1
    disrupted_ctry =  ['NLD']
    disrupted_sctr = ['i'+str(n+1) for n in range(25)]

    '''Create table and load all data'''
    DATA = Table('EORA_NLD',2010,list_countries)
    DATA.load_subset(curdir)

    '''Create model'''
    MRIA_RUN = MRIA(DATA.name,list_countries,DATA.sectors)
    
    '''Define sets and alias'''
    # CREATE SETS
    MRIA_RUN.create_sets()
    
    # CREATE ALIAS
    MRIA_RUN.create_alias()

    ''' Define tables and parameters'''
    Regmaxcap = 0.98

    output = pd.DataFrame()

    MRIA_RUN.baseline_data(DATA,disruption,disrupted_ctry,disrupted_sctr)
    MRIA_RUN.impact_data(DATA,disruption,disrupted_ctry,disrupted_sctr)
    output['x_in'] = pd.Series(MRIA_RUN.X.get_values())

#    MRIA_TZA.run_basemodel()
    MRIA_RUN.run_impactmodel()
    
    output['x_out'] = pd.Series(MRIA_RUN.X.get_values())
    output['loss'] = output['x_in'] - output['x_out']
  
    print(sum(output['loss']))

    '''
    VISUALIZE IT
    '''
    global_shap = gp.read_file('..\\global_shp\\TM_WORLD_BORDERS-0.3.shp')
    reg_loss = pd.DataFrame(output[['loss','x_in']].groupby(level=0).sum())
    reg_loss['loss_rel'] = (reg_loss['loss']/reg_loss['x_in'])*100 
    reg_loss['ISO3'] = reg_loss.index
    
    reg_loss['loss'] = reg_loss['loss'].round()
    reg_loss['loss_rel'] = reg_loss['loss_rel'].astype((np.float16))

    reg_shap = pd.merge(global_shap, reg_loss, on='ISO3', how='inner')
    reg_shap.plot(column='loss', cmap='OrRd', legend=True) 
    #reg_shap.to_file('TZA_example.shp')    
    #plt.savefig('TZA_example_MRIO.png',dpi=500)                  
    


