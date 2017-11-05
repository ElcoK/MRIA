# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 10:18:10 2017


This script builds the MRIA model using the EORA database as input

"""

from pyomo.environ import ConcreteModel,Set,SetOf,Param,Var,Constraint,Objective,minimize
import pandas as pd 
from pyomo.opt import SolverFactory
from mria_py.core.create_ratmarg import obtain_ratmarg


class MRIA(object):

    """
    This is the class object 'MRIA' which is used to set up the modelling framework.
    
    We define the type of model, sets, set up the core variables and specify the
    constraints and objectives for different model setups.
    """
    
    def __init__(self, name, list_countries,list_sectors,EORA=False):
 
        """
        Creation of a Concrete Model, specify the countries and sectors
        to include.
        """
        self.name = name
        self.m = ConcreteModel()
        self.countries = list_countries
        self.total_countries = len(list_countries)
        self.sectors = list_sectors
        if EORA is True:
            self.EORA = True
        else:
            self.EORA = False
   
    def create_sets(self,FD_SET=None,VA_SET=None):

        """
        Creation of the various sets. First step in future-proofing by allowing
        for own specification of set inputs
        """
        
        self.m.S = Set(initialize=self.sectors, doc='sectors')

        if self.EORA is True:
            self.m.rROW = Set(initialize=self.countries+['ROW'],ordered=True, doc='regions including export')
            self.m.R = Set(initialize=self.countries+['ROW'],ordered=True, doc='regions')
        else:
            self.m.rROW = Set(initialize=self.countries,ordered=True, doc='regions including export')
            self.m.R = Set(initialize=self.countries,ordered=True, doc='regions')

        if self.EORA is True:
            self.m.fdemand = Set(initialize=['P3h', 'P3n','P3g', 'P51','P52','P53'], doc='Final Demand')
        else:
            self.m.fdemand = Set(initialize=FD_SET, doc='Final Demand')

        if self.EORA is True:
            self.m.VA = Set(initialize=['VA'], doc='value added')
        else:
            self.m.VA = Set(initialize=VA_SET, doc='value added')

    def create_alias(self):
        """
        Set aliases
        """
        self.m.Rb   = SetOf(self.m.R)  # an alias of region R
        self.m.r   = SetOf(self.m.R)  # an alias of region R
        self.m.Sb   = SetOf(self.m.S)  # an alias of sector S


    """
    This part focuses on tables, parameters and variables
    """
    def create_A_mat(self,A_mat_in):
        model = self.m
        def A_matrix_init(model,R,S,Rb,Sb):
                    return A_mat_in[R,S,Rb,Sb]
        
        model.A_matrix = Param(model.R,model.S,model.R,model.Sb,initialize=A_matrix_init,doc = 'A matrix')

        self.A_matrix = model.A_matrix

    ''' Specify Final Demand and Local Final Demand'''
    def create_FD(self,FinalD):
        model = self.m
        def fd_init(model,R,S):
            return sum(FinalD[R,S,Rb,fdemand] for Rb in model.Rb for fdemand in model.fdemand)
     
        model.fd = Param(model.R, model.S, initialize=fd_init, doc='Final Demand')

        self.fd = model.fd
        
    ''' Specify local final demand '''
    def create_LFD(self,FinalD):
        model = self.m
        def lfd_init(model,R,S):
            return sum(FinalD[R,S,R,fdemand] for fdemand in model.fdemand)
        model.lfd = Param(model.R, model.S, initialize=lfd_init, doc='Final Demand')

        self.lfd = model.lfd        

    ''' Specify export and import to the rest of the world '''
    def create_ExpImp(self,ExpROW,ImpROW):
        model = self.m

        # Specify Export ROW
        def ExpROW_ini(m,R,S):
            return (ExpROW[R,S,'Export'])
        model.ExpROW = Param(model.R, model.S, initialize=ExpROW_ini, doc='Exports to the rest of the world')        
        
        # Specify Import ROW
        def ImpROW_init(m,R,S):
            return (ImpROW[R,S,'Import'])
        model.ImpROW = Param(model.R, model.S, initialize=ImpROW_init, doc='Imports from the rest of the world')        
 
        self.ExpROW = model.ExpROW
        self.ImpROW = model.ImpROW

    def create_ExpImp_EORA(self,Z_matrix):
        model = self.m

        # Specify Export ROW
        def ExpROW_ini(m,R,S):
            return (Z_matrix[R,S,'ROW','Total'])
        model.ExpROW = Param(model.R, model.S, initialize=ExpROW_ini, doc='Exports to the rest of the world')        
        
        # Specify Import ROW
        def ImpROW_init(m,R,S):
            return (Z_matrix['ROW','Total',R,S])
        model.ImpROW = Param(model.R, model.S, initialize=ImpROW_init, doc='Imports from the rest of the world')        
 
        self.ExpROW = model.ExpROW
        self.ImpROW = model.ImpROW


    """ Specify X variables """
    def create_X_up(self,disruption,disrupted_ctry,disrupted_sctr,Regmaxcap):
        model = self.m

        def shock_init(model, R,S):
            if R in disrupted_ctry and S in disrupted_sctr:
                return 1/Regmaxcap*disruption
            else:
                return 1/Regmaxcap*1.1       
               
        model.X_up = Param(model.R,model.S,initialize=shock_init, doc='Maximum production capacity')
        self.X_up = model.X_up

    '''create Xbase'''
    def create_Xbase(self,Z_matrix,FinalD=None):
        model = self.m

        if self.fd.active is not True:
            self.create_FD(FinalD)

        if self.ExpROW.active is not True:
            self.create_ExpImp(Z_matrix)

        def x_init_base(model,R,S):
            return( sum(Z_matrix[R,S,Rb,Sb] for Rb in model.Rb for Sb in model.Sb) + self.fd[R,S] + self.ExpROW[R,S])
    
        model.Xbase = Param(model.R, model.S,initialize=x_init_base,doc='Total Production baseline')
        self.Xbase = model.Xbase

    '''create X'''
    def create_X(self,disruption,disrupted_ctry,disrupted_sctr,A_matrix_ini=None,Z_matrix=None,FinalD=None,Xbase=None,fd=None,ExpROW=None,Regmaxcap=None):
        model = self.m

        if Regmaxcap is None:
            Regmaxcap = 0.98

        if self.Xbase.active is not True:
            self.create_Xbase(Z_matrix,FinalD)

        if self.A_matrix.active is not True:
            self.create_A_mat(A_matrix_ini)

        def X_bounds(model, R,S):
            if R in disrupted_ctry and S in disrupted_sctr:
                return (0.0, (1/Regmaxcap*self.Xbase[R,S])*disruption)
            else:
                return (0.0, (1/Regmaxcap*self.Xbase[R,S])*1.1)

        def x_init(model,R,S):
            return( sum(self.A_matrix[R,S,Rb,Sb]*self.Xbase[Rb,Sb] for Rb in model.Rb for Sb in model.Sb) + self.fd[R,S] + self.ExpROW[R,S])
            
        model.X = Var(model.R, model.S, bounds=X_bounds,initialize=x_init, doc='Total Production')
        
        self.X = model.X

    """ Specify trade and value added """

    ''' Specify Value Added '''
    def create_VA(self,ValueA):
        model = self.m

        def va_init(model,R,S):
            return ValueA[R,S,'VA']
        
        model.ValueA = Param(model.R, model.S, initialize=va_init, doc='Value Added')
        
        self.ValueA = model.ValueA
    

    ''' Specify Trade between regions '''
    def create_Z_mat(self):
        model = self.m
        def Z_matrix_init(model,R,S,Rb,Sb):
            return self.A_matrix[R,S,Rb,Sb]*self.X[Rb,Sb]   
        
        model.Z_matrix = Param(model.R,model.S,model.R,model.Sb,initialize=Z_matrix_init,doc = 'Z matrix')
        self.Z_matrix = model.Z_matrix

    def create_Trade(self,FinalD,Z_matrix=None):
        model = self.m

        def Trade_init(model,R,Rb,S):
            while R != Rb:
                return sum(self.Z_matrix[Rb,S,R,i] for i in model.Sb)  + sum(FinalD[Rb,S,R,i] for i in model.fdemand) 
            
        model.trade = Param(model.R,model.Rb, model.S, initialize=Trade_init, doc='Trade')        
        self.trade = model.trade

    '''Estimate Total Export'''
    def create_TotExp(self):
        model = self.m
        def totexp_init(model, R, S):
            return sum(self.trade[Rb,R,S] for Rb in model.Rb if (R != Rb))
        
        model.TotExp = Param(model.R, model.S,initialize=totexp_init,doc='Total exports between regions')
        self.TotExp = model.TotExp
    
    '''Estimate Total Import'''
    def create_TotImp(self):
        model = self.m
        def totimp_init(model, R, S):
            return sum(self.trade[R,Rb,S] for Rb in model.Rb if (R != Rb))
            
        model.TotImp = Param(model.R, model.S,initialize=totimp_init,doc='Total imports between regions')
        self.TotImp = model.TotImp
    
    '''Estimate Import shares and Import share DisImp'''
    def create_ImpShares(self):
        model = self.m
        def impsh_init(model, R, Rb, S):
            while self.trade[Rb,R,S] != None:
                return self.trade[Rb,R,S]/(sum(self.A_matrix[R,S,Rb,Sb]*self.X[Rb,Sb] for Sb in model.Sb) + self.fd[Rb,S])
                
        model.ImportShare = Param(model.R, model.Rb, model.S,initialize=impsh_init,doc='Importshare of each region')
        model.ImportShareDisImp = Param(model.R, model.Rb,model.S,initialize=impsh_init,doc='Importshare DisImp of each region')

        self.ImportShare = model.ImportShare
        self.ImportShareDisImp = model.ImportShareDisImp

    """ Specify specific variables for impact analysis """
    
    '''Reconstruction demand variable'''
    def create_Rdem(self):  
        model = self.m
        model.Rdem = Param(model.R, model.S,initialize=0, doc='Reconstruction demand')
        self.Rdem = model.Rdem

    '''Rationing variable'''
    def create_Rat(self,FinalD=None,Z_matrix=None):
        model = self.m
        
        if self.lfd.active is not True:
            self.create_LFD(FinalD)

        if self.ExpROW.active is not True:
            self.create_ExpImp(Z_matrix)     
        
        def Rat_bounds(model,R,S):
            return (0,abs(self.lfd[R,S]+self.ExpROW[R,S])) 
        
        model.Rat = Var(model.R, model.S,bounds=Rat_bounds,initialize=0,doc='Rationing')
        self.Rat = model.Rat

    def create_Ratmarg(self,Table):
        model = self.m

        try:
            RatMarg = pd.read_csv('..\..\input_data\Ratmarg_%s.csv' % self.name, index_col =[0],header=0)
            if self.EORA is True and (set(list(RatMarg.index.values)) != set(list(self.countries+['ROW']))):
                RatMarg = obtain_ratmarg(Table,self.EORA)
            elif (set(list(RatMarg.index.values)) != set(list(self.countries))):
                RatMarg = obtain_ratmarg(Table,self.EORA)
        except:
            RatMarg = obtain_ratmarg(Table,self.EORA)
 
        Ratmarginal = {(r,k): v for r, kv in RatMarg.iterrows() for k,v in kv.to_dict().items()}
 
        model.Ratmarg = Param(model.R, model.S,initialize=Ratmarginal, doc='Rationing marginal',mutable=True)
        self.Ratmarg = model.Ratmarg

    '''Disaster import variable'''
    def create_DisImp(self,disrupted_ctry,Regmaxcap=None):
        model = self.m

        if Regmaxcap is None:
            Regmaxcap = 0.98

        #problem regions
        dimp_ctry = ['KEN','UGA']
        dimp_ind = ['i3']

        def Dis_bounds(model,R,S):
            if R in dimp_ctry and S in dimp_ind:
                return (0,0)
            elif (model.X_up[R,S] < (1/Regmaxcap*1.1) or R in disrupted_ctry):
                return (0,None)
            else:
                return (0,None)
                        
        model.DisImp = Var(model.R, model.S,bounds=Dis_bounds,initialize=0, doc='Disaster Imports')
        self.DisImp = model.DisImp
        
    '''Specify demand function'''
    def create_demand(self):
        model = self.m

        def demand_init(model,R,S):
            return  (
            sum(self.A_matrix[R,S,R,Sb]*self.X[R,Sb] for Sb in model.Sb) + self.lfd[R,S] + self.Rdem[R,S] - self.Rat[R,S]
            +  sum(self.ImportShare[R,Rb,S]*(sum(self.A_matrix[R,S,Rb,Sb]*self.X[Rb,Sb] for Sb in model.Sb) + self.fd[Rb,S] + self.Rdem[Rb,S]- self.Rat[R,S]) for Rb in model.Rb if (R != Rb))
            +  sum(self.ImportShare[R,Rb,S]*(self.DisImp[Rb,S]) for Rb in model.Rb if (R != Rb))
            + self.ExpROW[R,S]
            )

        model.Demand = Var(model.R, model.S, bounds=(0.0,None),initialize=demand_init)  
        self.Demand = model.Demand

    """ Create baseline dataset to use in model """
    def baseline_data(self,Table,disruption=None,disrupted_ctry=None,disrupted_sctr=None,EORA=None):

        if disruption is None:
            disruption = 1.1
            disrupted_ctry = []
            disrupted_sctr = []

        if self.EORA is True:
            self.create_ExpImp_EORA(Table.Z_matrix)
        else:
            self.create_ExpImp(Table.ExpROW,Table.ImpROW)

        self.create_A_mat(Table.A_matrix)
        self.create_FD(Table.FinalD)
        self.create_LFD(Table.FinalD)
        self.create_Xbase(Table.Z_matrix,Table.FinalD)
        self.create_X(disruption,disrupted_ctry,disrupted_sctr,Table.Z_matrix,Table.FinalD)
        self.create_VA(Table.ValueA)
        self.create_Z_mat()
        self.create_Trade(Table.FinalD)
        self.create_TotExp()
        self.create_TotImp()
        self.create_ImpShares()

    """ Create additional parameters and variables required for impact
    analysis """
    def impact_data(self,Table,disruption,disrupted_ctry,disrupted_sctr,Regmaxcap=None):

        if Regmaxcap is None:
            Regmaxcap  = 0.98
        
        self.create_X_up(disruption,disrupted_ctry,disrupted_sctr,Regmaxcap)
        self.create_Rdem()
        self.create_Rat(Table.FinalD,Table.Z_matrix)
        self.create_Ratmarg(Table)
        self.create_DisImp(disrupted_ctry)
        self.create_demand()

    """
    Set up baseline model
    """
    def run_basemodel(self,solver=None):
        model = self.m

        if solver is None:
            solver = 'ipopt'

        def demSup(model, R,S):
            return  (self.X[R,S] >= 
                     sum(self.A_matrix[R,S,R,Sb]*self.X[R,Sb] for Sb in model.Sb) + self.lfd[R,S]
            +  sum(self.ImportShare[R,Rb,S]*(sum(self.A_matrix[R,S,Rb,Sb]*self.X[Rb,Sb] for Sb in model.Sb) + self.fd[Rb,S]) for Rb in model.Rb if (R != Rb))
#            + self.TotExp[R,S]
            + self.ExpROW[R,S])

        model.demSup = Constraint(model.R,model.S, rule=demSup, doc='Satisfy demand')
        
        def objective_base(model):
            return sum(self.X[R,S] for R in model.R for S in model.S)

        model.objective = Objective(rule=objective_base, sense=minimize, doc='Define objective function')

        opt = SolverFactory(solver)
        if solver is 'ipopt':
            opt.options['warm_start_init_point'] = 'yes'
            opt.options['warm_start_bound_push'] = 1e-6
            opt.options['warm_start_mult_bound_push'] = 1e-6
            opt.options['mu_init'] = 1e-6
        results = opt.solve(model,tee=True)
        #sends results to stdout
        results.write()

    def run_impactmodel(self,solver=None,tol=None,output=None,DisWeight=None,RatWeight=None):
        model = self.m

        if solver is None:
            solver = 'ipopt'

        if DisWeight is None:
            DisWeight = 1.75
        
        if RatWeight is None:
            RatWeight = 2

        def demDisRat(model, R,S):
            return  (
            self.Demand[R,S] ==  (sum(self.A_matrix[R,S,R,Sb]*self.X[R,Sb] for Sb in model.Sb) + self.lfd[R,S] + self.Rdem[R,S] - self.Rat[R,S]
            +  sum(self.ImportShare[R,Rb,S]*(sum(self.A_matrix[R,S,Rb,Sb]*self.X[Rb,Sb] for Sb in model.Sb) + self.fd[Rb,S] + self.Rdem[Rb,S]- self.Rat[Rb,S]) for Rb in model.Rb if (R != Rb))
            +  sum(self.ImportShare[R,Rb,S]*(self.DisImp[Rb,S]) for Rb in model.Rb if (R != Rb))
            + self.ExpROW[R,S]            )
            )

        model.demDisRat = Constraint(model.R,model.S, rule=demDisRat, doc='Satisfy demand')

        def demsupDis(model,R,S):
             return (self.DisImp[R,S]+self.X[R,S]) >= self.Demand[R,S]

        model.demsupDis = Constraint(model.R,model.S, rule=demsupDis, doc='Satisfy demand')

        def DisImpA(model,R,S):
            return (self.DisImp[R,S]*(self.DisImp[R,S] + (self.Xbase[R,S]*self.X_up[R,S]) - self.Demand[R,S])) == 0
        
        model.DisImpA = Constraint(model.R,model.S, rule=DisImpA, doc='Satisfy demand')

        def ObjectiveDis2(model):
            return (
                sum(self.X[R,S] for S in model.S for R in model.R)
                + DisWeight*sum((self.Ratmarg[R,S]*self.DisImp[R,S]) for R in model.R for S in model.S)
                + RatWeight*sum((self.Ratmarg[R,S]*self.Rat[R,S]) for R in model.R for S in model.S)
                + sum((sum(self.ImportShare[R,Rb,S]*(sum(self.A_matrix[R,S,Rb,Sb]*self.X[Rb,Sb] for Sb in model.Sb) + self.fd[Rb,S] + self.Rdem[Rb,S] - self.Rat[Rb,S]) for Rb in model.Rb if (R != Rb))
                +  sum(self.ImportShare[R,Rb,S]*(self.DisImp[Rb,S]) for Rb in model.Rb if (R != Rb))) for R in model.R for S in model.S)
                )    

        model.objective = Objective(rule=ObjectiveDis2, sense=minimize, doc='Define objective function')

        opt = SolverFactory(solver)
        if solver is 'ipopt':
            opt.options['max_iter'] = 5000
            opt.options['warm_start_init_point'] = 'yes'
            opt.options['warm_start_bound_push'] = 1e-6
            opt.options['warm_start_mult_bound_push'] = 1e-6
            opt.options['mu_init'] = 1e-6
            if tol is None:
                opt.options['tol'] = 1e-6
            else:
                opt.options['tol'] = tol
            
        if output is None:
            opt.solve(model,tee=False)
        else:
            results = opt.solve(model,tee=False)
            #sends results to stdout
            results.write()


    