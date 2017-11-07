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
import numpy as np
import sys

curdir = os.getcwd()
mria_path = r'C:\Dropbox\Oxford\MRIA\mria_py'  
if not mria_path in sys.path:
    sys.path.append(mria_path)

if __name__ == '__main__':

    _mriapath = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, _mriapath + '/../../')    

    from mria_py.core.create_table import Table_EORA
    from mria_py.core.base_model import MRIA
    from mria_py.core.visualize import visualize
    from mria_py.core.basic_IO import basic_IO
    

    '''Specify which countries should be included in the subset'''
    list_countries = ['TZA','KEN','RWA','UGA','COD','ZMB','MWI','MOZ']

    '''Create table and load all data'''
    DATA = Table_EORA('EORA_TZA',2010,list_countries)
    DATA.prep_data(curdir)

    '''Specify disruption'''
    disruption = 1.1
    disrupted_ctry =  ['TZA']
    disrupted_sctr = ['i'+str(n+1) for n in range(25)]

    '''Create model'''
    EORA=True
    MRIA_RUN = MRIA(DATA.name,list_countries,DATA.sectors,EORA)
    
    '''Define sets and alias'''
    # CREATE SETS
    MRIA_RUN.create_sets()
    
    # CREATE ALIAS
    MRIA_RUN.create_alias()

    ''' Define tables and parameters'''
    Regmaxcap = 0.98

    output = pd.DataFrame()
    output['x_in'] = pd.Series(MRIA_RUN.X.get_values())
    MRIA_RUN.baseline_data(DATA,disruption,disrupted_ctry,disrupted_sctr)
    MRIA_RUN.impact_data(DATA,disruption,disrupted_ctry,disrupted_sctr)
    output['x_in'] = pd.Series(MRIA_RUN.X.get_values())

    MRIA_RUN.run_impactmodel()
    
    output['x_out'] = pd.Series(MRIA_RUN.X.get_values())
    output['loss'] = output['x_in'] - output['x_out']
  
    print(sum(output['loss']))

    '''
    VISUALIZE IT
    '''
    global_shap = gp.read_file('..\\..\\global_shp\\TM_WORLD_BORDERS-0.3.shp')
    reg_loss = pd.DataFrame(output[['loss','x_in']].groupby(level=0).sum())
    reg_loss['loss_rel'] = (reg_loss['loss']/reg_loss['x_in'])*100 
    reg_loss['ISO3'] = reg_loss.index
    
    reg_loss['loss'] = reg_loss['loss'].round()
    reg_loss['loss_rel'] = reg_loss['loss_rel'].astype((np.float16))

    reg_shap = pd.merge(global_shap, reg_loss, on='ISO3', how='inner')
    reg_shap.plot(column='loss', cmap='OrRd', legend=True) 
    #reg_shap.to_file('TZA_example.shp')    
    #plt.savefig('TZA_example_MRIO.png',dpi=500)                  


