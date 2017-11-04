# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 15:11:16 2017

@author: cenv0574
"""

import os
import pandas as pd
from gams import GamsWorkspace, GamsParameter
import sys
from create_table import Table,Table_EORA

def load_base_db(Table,EORA=False,RoW=None):

    '''CREATE GAMS WORKSPACE'''
    
    ws = GamsWorkspace('..\\gams_runs\\')
    
    ''' CREATE INPUT FILES GAMS GDX '''
    
    db = ws.add_database()
    
    #set regions
    reg = db.add_set("reg",1,"Regions")
    if EORA is True:
        for r in (Table.countries+['ROW']):
            reg.add_record(r)
    else:
        for r in (Table.countries):
            reg.add_record(r)        
   
    #set rowcol
    rowcol = db.add_set("rowcol",1,"All rows and columns")   
    if EORA is True:
        industries = list(Table.sectors)  + ['Total']
        final_demand = list(Table.FD_labels['FD'].unique())

    else:
        industries = list(Table.sectors)  
        final_demand = list(Table.FD_labels['tfd'].unique())

    Import_lab  = ['Import']
    Export_lab  = ['Export']
    VA_lab = ['VA']
    
    rowcol_input = industries + final_demand + VA_lab + Import_lab + Export_lab
    for r in (rowcol_input):
        rowcol.add_record(r) 
    
    #set row
    row = db.add_set("row",1,"All rows")    
    row_input = industries + VA_lab + Import_lab
    for r in (row_input):
        row.add_record(r) 
      
    #set col
    col = db.add_set("col",1,"All columns")    
    col_input = industries + final_demand 
    for r in (col_input):
        col.add_record(r) 
        
    #set industries
    industries_ = db.add_set("S",1,"Industries")
    for r in  industries:
        industries_.add_record(r)    
    
    #set FinalD
    fd_ = GamsParameter(db,"FinDem_ini", 4, "FinDem")
    for k, v in Table.FinalD.items():
        fd_.add_record(k).value = v    
    
    #set interaction matrix of intermediate demand
    z_m = db.add_parameter("Z_matrix_ini", 4, "Interaction matrix")
    for k, v in Table.Z_matrix.items():
        z_m.add_record(k).value = v 
    
    #set interaction matrix of intermediate demand
    a_m = db.add_parameter("A_matrix_ini", 4, "A matrix")
    for k, v in Table.A_matrix.items():
        a_m.add_record(k).value = v 

    if EORA is False:
        #set Export ROW
        exp = db.add_parameter("ExpROW_ini", 4, "Exports to ROW")
        for k, v in Table.ExpROW.items():
            exp.add_record(k).value = v 
    
    #set ValueA
    val = db.add_parameter("ValueA_ini", 3, "Value Added")
    for k, v in Table.ValueA.items():
        val.add_record(k).value = v 
        
    # And save to GDX file
    db.export(("..\\gams_runs\\%s.gdx" % Table.name))

def obtain_ratmarg(Table,EORA=False):

    if EORA is True:
        Table.load_subset()
        load_base_db(Table,EORA=True)
    else:
        Table.prep_data()
        load_base_db(Table)
    
    '''
    RUN SCRIPT WITH DISRUPTION
    '''

    ws = GamsWorkspace('..\\gams_runs\\')
    
    if EORA is False:
        gamsfile = "..\\gams_runs\\obtain_marg_value_Vale.gms"
        str_ctry = ','.join(Table.countries)    
    else:
        gamsfile = "..\\gams_runs\\obtain_marg_value.gms"
        str_ctry = ','.join(Table.countries+['ROW']) 

    with open(gamsfile, 'r') as file:
        # read a list of lines into data
        data = file.readlines()

    data[34] = '/'+str_ctry+'/\n'
    data[36] = '/'+str_ctry+'/\n'

    with open(gamsfile, 'w') as file:
        file.writelines( data )
    
    t1 = ws.add_job_from_file(gamsfile)
    
    t1.run()
    
    Ratmarg = []
    index_ = []
    for rec in t1.out_db["Ratmarg"]:
        index_.append((rec.keys[0],rec.keys[1]))
        Ratmarg.append(rec.get_value())     
        
    index_ = pd.MultiIndex.from_tuples(index_, names=('CNTRY', 'IND'))
    Ratmarginal = pd.DataFrame(Ratmarg, index=index_).unstack()
    Ratmarginal.columns = Ratmarginal.columns.droplevel()

    Ratmarginal.to_csv('..\input_data\Ratmarg_%s.csv' % Table.name)


    return Ratmarginal    

if __name__ == '__main__':

    '''Specify which countries should be included in the subset'''

    list_countries = ['Elms','Hazel','Montagu','Fogwell','Riverside','Oatlands']

    filepath = '..\input_data\The_Vale.xlsx'

    # CREATE MODEL
    TheVale = Table('TheVale',filepath,2010,list_countries)
    
    Ratmarginal = obtain_ratmarg(TheVale)

    list_countries = ['TZA','KEN','RWA','UGA','COD','ZMB','MWI','MOZ']
    list_sectors = ['i'+str(n+1) for n in range(26)]

    # CREATE MODEL
    EORA_TZA = Table_EORA('EORA_TZA',2010,list_countries)
    
    Ratmarginal = obtain_ratmarg(EORA_TZA,EORA=True)
    
#    out = list(RatMarg.index.values)
    
#    set(list_countries) == set(out)