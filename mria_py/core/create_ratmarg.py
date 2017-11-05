# -*- coding: utf-8 -*-
"""
Create output file for gams and run a quick gams module to estimate marginal values of rationing demand

@author: Elco Koks

@date: Nov, 2017
"""

import pandas as pd
from gams import GamsWorkspace, GamsParameter
from mria_py.core.create_table import Table,Table_EORA,Table_OECD
from shutil import copyfile


def load_base_db(table_in,EORA=False,RoW=None):

    '''CREATE GAMS WORKSPACE'''
    
    ws = GamsWorkspace('..\\..\\gams_runs\\')
    
    ''' CREATE INPUT FILES GAMS GDX '''
    
    db = ws.add_database()
    
    #set regions
    reg = db.add_set("reg",1,"Regions")
    if EORA is True:
        for r in (table_in.countries+['ROW']):
            reg.add_record(r)
    else:
        for r in (table_in.countries):
            reg.add_record(r)        
   
    #set rowcol
    rowcol = db.add_set("rowcol",1,"All rows and columns")   
    if EORA is True:
        industries = list(table_in.sectors)  + ['Total']
        final_demand = list(table_in.FD_labels['FD'].unique())

    else:
        industries = list(table_in.sectors)  
        final_demand = list(table_in.FD_labels['tfd'].unique())

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
    for k, v in table_in.FinalD.items():
        fd_.add_record(k).value = v    
    
    #set interaction matrix of intermediate demand
    z_m = db.add_parameter("Z_matrix_ini", 4, "Interaction matrix")
    for k, v in table_in.Z_matrix.items():
        z_m.add_record(k).value = v 
    
    #set interaction matrix of intermediate demand
    a_m = db.add_parameter("A_matrix_ini", 4, "A matrix")
    for k, v in table_in.A_matrix.items():
        a_m.add_record(k).value = v 

    if EORA is not True:
        #set Export ROW
        exp = db.add_parameter("ExpROW_ini", 3, "Exports to ROW")
        for k, v in table_in.ExpROW.items():
            exp.add_record(k).value = v 
    
    #set ValueA
    val = db.add_parameter("ValueA_ini", 3, "Value Added")
    for k, v in table_in.ValueA.items():
        val.add_record(k).value = v 
        
    # And save to GDX file
    db.export(("..\\gams_runs\\%s.gdx" % table_in.name))

def obtain_ratmarg(table_in,EORA=False):

    table_in.prep_data()

    if EORA is True:
        load_base_db(table_in,EORA=True)
    else:
        load_base_db(table_in)
    
    '''
    RUN SCRIPT WITH DISRUPTION
    '''
    setdir = '..\\..\\gams_runs\\'
    ws = GamsWorkspace(setdir)
    ws.get_working_directory()
    
    if EORA is False:
        gamsfile_in = "..\\..\\gams_runs\\obtain_marg_value.gms"
        gamsfile = "..\\..\\gams_runs\\obtain_marg_value_%s.gms" %(table_in.name)
        copyfile(gamsfile_in, gamsfile)
        str_ctry = ','.join(table_in.countries)    
        str_fd = ','.join(list(table_in.FD_labels['tfd'].unique()))

    else:
        gamsfile_in = "..\\..\\gams_runs\\obtain_marg_value_EORA.gms"
        gamsfile = "..\\..\\gams_runs\\obtain_marg_value_%s.gms" %(table_in.name)
        copyfile(gamsfile_in, gamsfile)
        str_ctry = ','.join(table_in.countries+['ROW']) 
        str_fd = ','.join(list(table_in.FD_labels['FD'].unique()))


    with open(gamsfile, 'r') as file:
        # read a list of lines into data
        data = file.readlines()

    gdx_file = "%s.gdx" % table_in.name
    data[26] = '$GDXIN '+gdx_file+'\n'

    str_ind = ','.join(table_in.sectors) 
    data[32] ='S(col) list of industries  /'+str_ind+'/\n'


    data[34] = '/'+str_ctry+'/\n'
    data[36] = '/'+str_ctry+'/\n'
    data[38]  = '/'+str_fd+'/\n'

    with open(gamsfile, 'w') as file:
        file.writelines( data )
    
    gamsfile_run = gamsfile.replace("..\\..\\gams_runs\\", "")
    t1 = ws.add_job_from_file(gamsfile_run)
    
    t1.run()
    
    Ratmarg = []
    index_ = []
    for rec in t1.out_db["Ratmarg"]:
        index_.append((rec.keys[0],rec.keys[1]))
        Ratmarg.append(rec.get_value())     
        
    index_ = pd.MultiIndex.from_tuples(index_, names=('CNTRY', 'IND'))
    Ratmarginal = pd.DataFrame(Ratmarg, index=index_).unstack()
    Ratmarginal.columns = Ratmarginal.columns.droplevel()

    Ratmarginal.to_csv('..\\..\\input_data\\Ratmarg_%s.csv' % table_in.name)


    return Ratmarginal    

if __name__ == '__main__':

    '''Specify which countries should be included in the subset'''
    list_countries = ['TZA','KEN','RWA','UGA','COD','ZMB','MWI','MOZ']
#    list_countries = ['Elms','Hazel','Montagu','Fogwell','Riverside','Oatlands']


    '''Create table and load all data'''
    DATA = Table_EORA('EORA_TZA',2010,list_countries)
    DATA.prep_data()

    Ratmarginal = obtain_ratmarg(DATA,EORA=True)
    

#    filepath = '..\input_data\The_Vale.xlsx'

    # CREATE MODEL
#    TheVale = Table('TheVale',filepath,2010)
#    TheVale.prep_data()
#    load_base_db(TheVale)
#    Ratmarginal = obtain_ratmarg(TheVale)

#    filepath = '..\input_data\ICIO_2016_2011.csv'

#    OECD = Table_OECD('OECD',filepath,2010)
#    OECD.prep_data()
#    Ratmarginal = obtain_ratmarg(OECD)
