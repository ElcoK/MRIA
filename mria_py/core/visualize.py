# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 15:55:43 2017

@author: elcok
"""
import seaborn as sns
import pandas as pd
from mria_py.core.create_table import Table
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

matplotlib.style.use('ggplot')

class visualize(object):
    
        """
        This class allows for some basic visualisation with the IO table
        """
        def __init__(self, data):
            self.countries = data.countries
            self.total_countries = len(data.countries)
            self.sectors = data.sectors    
            self.data = data
            
        def heatmap(self,table_part='Z'):

            if table_part == 'Z':
                self.data.T_data.index.names = ['Region','Industry']
                self.data.T_data.columns.names = ['Region','Industry']
                heatmap = sns.heatmap(self.data.T_data, linewidths=0.2, linecolor='white',
                                   cmap='YlGnBu')  
                return heatmap

            elif table_part == 'FD':
                self.data.FD_data.index.names = ['Region','Industry']
                self.data.FD_data.columns.names = ['Region','FinDem']
                heatmap = sns.heatmap(self.data.FD_data, linewidths=0.2, linecolor='white',
                                   cmap='YlGnBu')  
                return heatmap            

        def barplot(self,table_part='full',region='all',industry='all'):
                
            if region == 'all' and industry == 'all':
                if table_part == 'full':
                    return self.data.sum_data.plot.bar()
                elif table_part == 'Z':
                    return self.data.T_data.sum(axis=1).plot.bar()
                elif table_part == 'FD':
                    return self.data.FD_data.sum(axis=1).plot.bar()
            
            if region == 'all' and industry != 'all':
                if table_part == 'Z':
                    return self.data.T_data.sum(axis=1).xs(industry,level=1).plot.bar()
                elif table_part == 'FD':
                    return self.data.FD_data.sum(axis=1).xs(industry,level=1).plot.bar()         

            if industry == 'all' and region != 'all':
                if table_part == 'Z':
                    return self.data.T_data.sum().xs(region,level=0).plot.bar()
                elif table_part == 'FD':
                    return self.data.FD_data.sum().xs(region,level=0).plot.bar()            

            
if __name__ == '__main__':


    ''' Specify file path '''
    filepath = '..\..\input_data\The_Vale.xlsx'

    '''Specify which countries should be included in the subset'''

    list_countries = ['Elms','Hazel','Montagu','Fogwell','Riverside','Oatlands']


    '''Create data input'''
    data = Table('TheVale',filepath,2010)
    data.prep_data()
    
    visualize(data).barplot(table_part='Z',region='all',industry='Agri')
    

