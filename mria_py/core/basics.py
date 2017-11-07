# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 14:05:32 2017

@author: elcok
"""

import pandas as pd 
import numpy as np


class basic_IO(object):
    
        """
        This class allows to do some basic IO calculations with the data
        """
        
        def __init__(self, data):
            self.countries = data.countries
            self.total_countries = len(data.countries)
            self.sectors = data.sectors    
            self.data = data

        def Leontief_inverse(self):
            '''Estimate the Leontief Inverse'''
            
            I_mat = np.identity((len(self.data.A))) # Iden
            linverse = np.linalg.inv(I_mat - self.data.A)
            
            return pd.DataFrame(linverse,index=self.data.T_labels,columns=self.data.T_labels)

        def check_table(self):
            '''Check if table is balanced'''
            
            linverse = self.Leontief_inverse()
            tfd = self.data.FD_data.sum(axis=1) + self.data.ExpROW_data.sum(axis=1)
            linverse.dot(tfd)

            diff = sum(linverse.dot(tfd)-self.data.sum_data)
            
            if diff < 1e-2:
                return print('The table is balanced')
            else:
                return print('The table is not balanced. The difference is %s. Please check the tables again.' % diff)
        

    
    
