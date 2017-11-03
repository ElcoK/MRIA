# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 15:11:16 2017

@author: cenv0574
"""

import os
import pandas as pd
from gams import GamsWorkspace, GamsParameter
import sys
from EORA_TABLE import Table

def load_base_db(Table):

    '''CREATE GAMS WORKSPACE'''
    
    ws = GamsWorkspace('..\\gams_runs\\')
    
    ''' CREATE INPUT FILES GAMS GDX '''
    
    db = ws.add_database()
    
    #set regions
    reg = db.add_set("reg",1,"Regions")
    for r in (Table.countries+['ROW']):
        reg.add_record(r)
    
    #set rowcol
    rowcol = db.add_set("rowcol",1,"All rows and columns")   
    industries = list(Table.sectors)  + ['Total']
    final_demand = list(Table.FD_labels['FD'].unique())
    Export_lab = ['Export']
    VA_lab = ['VA']
    Import_lab  = ['Import']
    
    rowcol_input = industries + final_demand + Export_lab + VA_lab + Import_lab
    for r in (rowcol_input):
        rowcol.add_record(r) 
    
    #set row
    row = db.add_set("row",1,"All rows")    
    row_input = industries + VA_lab + Import_lab
    for r in (row_input):
        row.add_record(r) 
      
    #set col
    col = db.add_set("col",1,"All columns")    
    col_input = industries + final_demand + Export_lab
    for r in (col_input):
        col.add_record(r) 
        
    #set industries
    industries_ = db.add_set("S",1,"Industries")
    for r in  industries:
        industries_.add_record(r)    
    
    #set FinalD
    fd_ = GamsParameter(db,"FinDem_ini", 4, "FinDem EORA 2010")
    for k, v in Table.FinalD.items():
        fd_.add_record(k).value = v    
    
    #set interaction matrix of intermediate demand
    z_m = db.add_parameter("Z_matrix_ini", 4, "Interaction matrix EORA 2010")
    for k, v in Table.Z_matrix.items():
        z_m.add_record(k).value = v 
    
    #set interaction matrix of intermediate demand
    z_m = db.add_parameter("A_matrix_ini", 4, "A matrix EORA 2010")
    for k, v in Table.A_matrix.items():
        z_m.add_record(k).value = v 
    
    #set ValueA
    val = db.add_parameter("ValueA_ini", 3, "Value Added EORA 2010")
    for k, v in Table.ValueA.items():
        val.add_record(k).value = v 
        
    # And save to GDX file
    db.export(("..\\gams_runs\\EORA_2010_TZA_ROW.gdx"))

def obtain_ratmarg(Table):
   
    Table.load_subset()
    load_base_db(Table)
    
    '''
    RUN SCRIPT WITH DISRUPTION
    '''

    ws = GamsWorkspace('..\\gams_runs\\')
    
    with open("..\\gams_runs\\obtain_marg_value.gms", 'r') as file:
        # read a list of lines into data
        data = file.readlines()

    str_ctry = ','.join(Table.countries+['ROW'])    
    data[34] = '/'+str_ctry+'/\n'
    data[36] = '/'+str_ctry+'/\n'

    with open("..\\gams_runs\\obtain_marg_value.gms", 'w') as file:
        file.writelines( data )
    
    t1 = ws.add_job_from_file("..\\gams_runs\\obtain_marg_value.gms")
    
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

    curdir = os.getcwd()
        
    list_countries = ['TZA','KEN','RWA','UGA','COD','ZMB','MWI','MOZ']
    list_sectors = ['i'+str(n+1) for n in range(26)]

    # CREATE MODEL
    EORA_TZA = Table('EORA_TZA',2010,list_countries)
    
    Ratmarginal = obtain_ratmarg(EORA_TZA)
    
#    out = list(RatMarg.index.values)
    
#    set(list_countries) == set(out)