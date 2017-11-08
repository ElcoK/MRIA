
* DEFINE SETS AND PARAMETERS TO BE IMPORTED FROM FILE
sets
         rowcol(*) all rows and columns
         row(rowcol) rows supply
         col(rowcol) columns industry
         OnlyS(col)
         reg all_regions
         r specified regions
         va value added /VA/
         export /Exports/
         import /Imports/
;


* SET ALIAS FOR THESE SETS
Alias(rowcol,rowcol2)  ;
Alias(reg,reg2)        ;
Alias(r,Rb,Rc,region)  ;

* LOAD BASE DATA
Parameter
         REG_USE2013(reg,rowcol,reg2,rowcol),
         REG_SUP2013(reg,rowcol,reg2,rowcol),
         ValueA_ini(reg,row,va),
         ExpROW_ini(reg,row,export)
         ImpROW_ini(reg,col,import)
;

* IMPORT SETS AND SUPPLY - USE TABLES
$GDXIN TheVale_SuT.gdx
$LOAD reg,rowcol,row,col,REG_USE2013,REG_SUP2013,ExpROW_ini,ValueA_ini,ImpROW_ini
$GDXIN

* DEFINE SETS AND PARAMETERS TO BE IMPORTED FROM FILE
set
         rROW(reg) The region subset plus ROW for the cost estimation
/Montagu,Oatlands,Hazel, Elms,Fogwell,Riverside     /
         r(rROW) The region subset used in this analysis
/Montagu,Oatlands,Hazel, Elms,Fogwell,Riverside     /
         ind(col) /Agri,Manu,Comm,NonComm/
         p(row)  /AgriP,ManuP,CommP,NonCommP/
         fdemand(col) final demand
/FinalD/
         PNL(p)
;

Alias(reg,reg2)
Alias(rROW,rROWb);
Alias(p,p2,P)          ;
Alias(ind,S,Sb)        ;
Alias(r,Rb,Rc,region)  ;

PNL(p) = yes

Scalar Regmaxcap,test_diff,Xdiff

Parameter
         FinDem(R,P) Final demand, Use(R,P,S) Use Tables Technical coefficienties,
         ValueA(R,S) ValueAdded, Sup(R,S,P) Supply Tables production coefficients,
         Trade(R,Rb,P) Trade Table, VAshare(R,S) Value added share in production,
         Expshare(R,Rb,P) Export destination shares, TotExp(r,p), TotImp(r,p),
         ExpROW(R,P),ImpROW(R,P),TotsupP(R,P) total supply, TotUse(R,P), TotSup(R,S),TotSupS(R,P)
         Importshare(R,Rb,P) Import Origin shares, ImportshareDisImp(R,Rb,P) Local import shares,
         ImportratioPar(R,P) Import versus local production , Tramar(r,p), taxes(r,p) ,
         OtherDem(R,P),RealOutput(R,P),RealDemand(R,P),RealUse(R,P) ,RealDiff(R,P),check_ratio(R,P),Tra_Tra(R,P),
         Tra_Tra2(R,P), Xbase(R,S), test_importratio1(R,P) ,TotUse(Rb,P) ,TotUse2(R,P),TotUse3(R,P),TotExp2(R,P),
         DisImpPar(R,P),Xmarg(R,S) Marginal value on producing les, RatMarg(R,P) Marginal value on rationing ,SumUse(R,P)
         tottotimp(r,p), tottotexp(r,p)   ,   UseAbs(R,row,col),  SupAbs(R,Rb,row,col)
         Trade2(R,Rb,P),TotUseS(R,S),TotUseS2(R,S),Shock(R,S),
         wS(R,S) waste per sector, TotProdP(R,P), TotP(R,P), TotS(R,S), ValueAdded(R,S),WSshare(R,S)
         Wshare(R,P), costP(R,P), cost(R) ,test(R,P), test2(R,P), Rdem(R,P,S) Reconstruction demand
         Trade2013(reg,reg2,P)

;
VARIABLE
         Z objective, DisImp1(R,P) Disaster Additional Imports
;
POSITIVE VARIABLE
         X(R,S) total production , Demand(R,P) demand,  XP(R,P) total products, Rationdem(R,P) Rationed demand,
         DisImp(R,P) Disaster Additional Imports,X_s(R,S);

* LOAD TOTALS OF DATA
TotSup(R,S) =   sum((reg,row), REG_SUP2013(reg,S,R,row))  ;
TotUseS(R,S) =   sum((reg,row), REG_USE2013(R,row,reg,S))  ;
*ValueA(R,S) = sum(va,ValueA_ini(R,S,va))  ;

* CREATE SUPPLY TABLE
Sup(R,S,P)$Totsup(R,S) = REG_SUP2013(R,S,R,P);
Sup(R,S,P)$Totsup(R,S) = Sup(R,S,P)$Totsup(R,S)/(Totsup(R,S))  ;

* CREATE TOTALS TAKE 2
X.L(R,S)  = sum((reg,row), REG_SUP2013(reg,S,R,row))  ;
XP.L(R,P) = sum(S, X.L(R,S)*Sup(R,S,P));

* CREATE USE TABLE
UseAbs(R,P,S)$X.L(R,S) = sum(reg,REG_USE2013(reg,P,R,S));
Use(R,P,S)$X.L(R,S) = UseAbs(R,P,S)$X.L(R,S)/X.L(R,S)  ;

* LOAD DEMAND
FinDem(R,P)=sum((reg,fdemand), REG_USE2013(reg,P,R,fdemand));

* ADD TRADE
Trade(R,Rb,P)$(ord(Rb)<>ord(R))  = sum(col,REG_USE2013(R,P,Rb,col));

* set baseline data for X and define Value added
Xbase(R,S)$([X.L(R,S) <> 0]) = X.L(R,S);

*VAshare(R,S) = ValueA(R,S)$X.L(R,S)/X.L(R,S)  ;

* LOAD EXPORTS
TotExp(R,P)=sum(Rb, Trade(R,Rb,P));
ExpROW(R,P) = ExpROW_ini(R,P,'Exports') ;
Expshare(R,Rb,P)$TotExp(r,p)=Trade(R,Rb,P)/TotExp(r,p);

* LOAD IMPORTS
TotImp(Rb,P)=sum(R, Trade(R,Rb,P));
ImpROW(R,P) = 0;
*ImpROW_ini(R,P,'Imports') ;
Importshare(R,Rb,P)$Totimp(Rb,P)=Trade(R,Rb,P)/Totimp(Rb,P);
ImportshareDisImp(R,Rb,P) = Importshare(R,Rb,P)           ;

* Estimate import ratio. This is where I've in the end changed a few things with regards to the trade and transport margins and taxes (Tra_Tra parameter)
*The OnlyTra makes sure that this only happens for these services, to have importratios which are below 1.
ImportratioPar(R,P) = 1;
ImportratioPar(R,P) = (TotImp(R,P)+ImpROW(R,P))/(sum(S, X.l(R,S)*Use(R,P,S))+ FinDem(R,P))    ;
ImportratioPar(R,P)$(ImportratioPar(R,P)>0.99999)=1;

* Baseline. this works for NL and UK, global and IT seem to be having problems with (mainly) C30 & H51
RealUse(R,P)  = (sum(S, X.l(R,S)*Use(R,P,S))  + FinDem(R,P))*(1-ImportratioPar(R,P))
                 + sum(Rb$(ord(Rb)<>ord(R)), Importshare(R,Rb,P)*((sum(S, X.L(Rb,S)*Use(Rb,P,S)) + FinDem(Rb,P))*((Totimp(Rb,P)/(Totimp(Rb,P)+ImpROW(Rb,P))*importratioPar(rb,p)))))
                 + ExpROW(R,P)
;

RealOutput(R,P) =   sum(S, X.L(R,S)*Sup(R,S,P));
RealDiff(R,P) = RealOutput(R,P) - RealUse(R,P);

* save baseline data
execute_unload 'TheVale.gdx' TotUseS,UseAbs,Shock,ValueA,UseAbs,RealOutput,RealDiff,RealUse,TotUse,FinDem,TotSup,X,XP,Use,Sup,TotExp,TotImp,ExpROW,ImpROW,Trade,Importshare,Expshare,ImportratioPar,Trade;

EQUATIONS
         demsup(R,P)             demand is equal to supply on the product level for every region
         Objective               The objective function
;

*PRE-DISASTER EQUATION:
demsup(R,P)..
       sum(S, X(R,S)*Sup(R,S,P))  =g= 0
       + (sum(S, X(R,S)*Use(R,P,S))  + FinDem(R,P))*(1-ImportratioPar(R,P))
                 + sum(Rb$(ord(Rb)<>ord(R)), Importshare(R,Rb,P)*((sum(S, X(Rb,S)*Use(Rb,P,S)) + FinDem(Rb,P))*((Totimp(Rb,P)/(Totimp(Rb,P)))*importratioPar(rb,p))))
                 + ExpROW(R,P);

Objective..
Z =e=
*Production costs
     sum((R,S), X(R,S))
    ;

MODEL
         LPIO base supply and use model /demsup,Objective/;


Rationdem.fx(R,P)=0;
Rdem(R,P,S) = 0;
DisImp.l(R,P)=0;

Demand.l(R,P) = 0
      + (sum(S, X.l(R,S)*Use(R,P,S)) + (sum(S,Rdem(R,P,S))) + FinDem(R,P))*(1-ImportratioPar(R,P))
                 + sum(Rb$(ord(Rb)<>ord(R)), Importshare(R,Rb,P)*((sum(S, X.L(Rb,S)*Use(Rb,P,S)) + (sum(S,Rdem(R,P,S))) + FinDem(Rb,P))*((Totimp(Rb,P)/(Totimp(Rb,P)+ImpROW(Rb,P)))*importratioPar(rb,p))))
                 + sum(Rb$(ord(Rb)<>ord(R)), ImportshareDisImp(R,Rb,P)*(Totimp(Rb,P)/(Totimp(Rb,P)+ImpROW(Rb,P)$PNL(p)))*DisImp.L(Rb,P))
                 + ExpROW(R,P);

* This is the baseline situation, this should give a solutation where Xdiff (see below) should be close to zero.

option LP=ipopt;
LPIO.OptFile = 1;
SOLVE LPIO minimizing Z using LP;

* CHECK IF DATA IS BALANCED
RealUse(R,P)  = (sum(S, X.l(R,S)*Use(R,P,S))  + FinDem(R,P))*(1-ImportratioPar(R,P))
                 + sum(Rb$(ord(Rb)<>ord(R)), Importshare(R,Rb,P)*((sum(S, X.L(Rb,S)*Use(Rb,P,S)) + FinDem(Rb,P))*((Totimp(Rb,P)/(Totimp(Rb,P)+ImpROW(Rb,P)))*importratioPar(rb,p))))
                 + ExpROW(R,P);


RealOutput(R,P) =   sum(S, X.L(R,S)*Sup(R,S,P));
RealDiff(R,P) = RealOutput(R,P) - RealUse(R,P);
test_diff =  sum((R,P),RealDiff(R,P));

Xdiff = sum((R,S),Xbase(R,S) - X.L(R,S));

execute_unload 'test.gdx' Xdiff,X,Xbase

EQUATIONS
         demDisRatMarg(R,P)      demand is equal to supply on the product level for every region
         ObjectiveMarg           The objective function
 ;

*POST-DISASTER EQUATION with demand rationing:
demDisRatMarg(R,P)..
       DisImp(R,P) + sum(S, X(R,S)*Sup(R,S,P))  =g= 0
       + (sum(S, X(R,S)*Use(R,P,S))  + FinDem(R,P)- Rationdem(R,P) + (sum(S,Rdem(R,P,S))))*(1-ImportratioPar(R,P))
                 + sum(Rb$(ord(Rb)<>ord(R)), Importshare(R,Rb,P)*((sum(S, X(Rb,S)*Use(Rb,P,S)) + FinDem(Rb,P) - Rationdem(Rb,P) + (sum(S,Rdem(Rb,P,S))))*((Totimp(Rb,P)/(Totimp(Rb,P)+ImpROW(Rb,P)))*importratioPar(rb,p))))
                 + sum(Rb$(ord(Rb)<>ord(R)), ImportshareDisImp(R,Rb,P)*(Totimp(Rb,P)/(Totimp(Rb,P)+ImpROW(Rb,P)$PNL(p)))*DisImp(Rb,P))
                 + ExpROW(R,P);

ObjectiveMarg..
Z =e=
*Production costs
     sum((R,P), sum(S, (X(R,S)*Sup(R,S,P))))
*Niet gratis uit de rest van de wereld:
     + sum((R,P),
       sum(Rb$(ord(Rb)<>ord(R)), Importshare(R,Rb,P)*((sum(S, X(Rb,S)*Use(Rb,P,S))  - Rationdem(Rb,P) + FinDem(Rb,P) + sum(S,Rdem(Rb,P,S)))*((Totimp(Rb,P)/(Totimp(Rb,P)+ImpROW(Rb,P)))*importratioPar(rb,p))))
      + sum(Rb$(ord(Rb)<>ord(R)), ImportshareDisImp(R,Rb,P)*(ImpROW(Rb,P)/(Totimp(Rb,P)+ImpROW(Rb,P)$PNL(p)))*DisImp(Rb,P))
        )
  ;

* DEFINE MODELS TO SOLVE:

MODEL
         LPIODisMarg supply and use model with endogenous imports but no maximum function /demDisRatMarg,ObjectiveMarg/;

LPIODISMarg.solvelink=5;
LPIODisMarg.workfactor=1.5 ;

Regmaxcap=0.98;
X.up(R,S)=1.10*(1/Regmaxcap)*Xbase(R,S)+1;
Rationdem.fx(R,P)=0;
DisImp.fx(R,P)=0;
X.lo(R,S)=0;
option LP=osiMosek;
SOLVE LPIODisMarg minimizing Z using LP;
Xmarg(R,S)=X.M(R,S);
Ratmarg(R,P)=Rationdem.M(R,P);
option NLP=conopt;
LPIODisMarg.OptFile = 1;
SOLVE LPIODisMarg minimizing Z using LP;
Xmarg(R,S)=X.M(R,S);
Ratmarg(R,P)=abs(Rationdem.M(R,P));
Ratmarg(R,P)$(Ratmarg(R,P)<1)=1;
display Xmarg,Ratmarg;
