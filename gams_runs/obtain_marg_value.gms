
* DEFINE SETS AND PARAMETERS TO BE IMPORTED FROM FILE
sets
         rowcol(*) all rows and columns
         row(rowcol) rows supply
         col(rowcol) columns industry
         OnlyS(col)
         reg all_regions
         r specified regions
;

* SET ALIAS FOR THESE SETS
Alias(rowcol,rowcol2)  ;
Alias(reg,reg2)        ;
Alias(r,Rb,Rc,region)  ;

* LOAD BASE DATA
Parameter
         Z_matrix_ini(reg,rowcol,reg2,rowcol)
         FinDem_ini(reg,rowcol,reg2,rowcol)
         ValueA_ini(reg,col,rowcol)
         ExpROW_ini(reg,rowcol,rowcol)
         ImpROW_ini(reg,col,rowcol)
         A_matrix_ini(reg,rowcol,reg2,rowcol)
 ;
* IMPORT SETS AND SUPPLY - USE TABLES
$GDXIN TheVale.gdx
$LOAD reg,rowcol,row,col,Z_matrix_ini,FinDem_ini,ValueA_ini,A_matrix_ini,ExpROW_ini
$GDXIN

* DEFINE OTHER ESSENTIAL SETS  (and create a subset for NL, which makes things go faster for checking)
set
         S(col) list of industries  /Agri,Comm,Manu,NonComm/
         rROW(reg) The region subset plus ROW for the cost estimation
/AUS,AUT,BEL,CAN,CHL,CZE,DNK,EST,FIN,FRA,DEU,GRC,HUN,ISL,IRL,ISR,ITA,JPN,KOR,LVA,LUX,MEX,NLD,NZL,NOR,POL,PRT,SVK,SVN,ESP,SWE,CHE,TUR,GBR,USA,ARG,BGR,BRA,BRN,CHN,COL,CRI,CYP,HKG,HRV,IDN,IND,KHM,LTU,MLT,MYS,MAR,PER,PHL,ROU,RUS,SAU,SGP,THA,TUN,TWN,VNM,ZAF,ROW,MX1,MX2,MX3,CN1,CN2,CN3,CN4/
         r(rROW) The region subset used in this analysis
/AUS,AUT,BEL,CAN,CHL,CZE,DNK,EST,FIN,FRA,DEU,GRC,HUN,ISL,IRL,ISR,ITA,JPN,KOR,LVA,LUX,MEX,NLD,NZL,NOR,POL,PRT,SVK,SVN,ESP,SWE,CHE,TUR,GBR,USA,ARG,BGR,BRA,BRN,CHN,COL,CRI,CYP,HKG,HRV,IDN,IND,KHM,LTU,MLT,MYS,MAR,PER,PHL,ROU,RUS,SAU,SGP,THA,TUN,TWN,VNM,ZAF,ROW,MX1,MX2,MX3,CN1,CN2,CN3,CN4/
         fdemand(col) final demand
/FinDem/
         v_a(row) value added /VA/
         slctd_regions(reg) selected regions only
;

Alias(ind,S,Sb)        ;
Alias(rROW,rROWb);
* Define some set specifics
slctd_regions(r)=yes;
OnlyS(ind) = yes;

* Create matrix to assess cost of the disaster
SET RSall /rs1*rs926/, rs(RSall), mapRS(r,s,rsall);



* SET SCALARS, PARAMETERS AND VARIABLES
SCALAR
         test_diff,Regmaxcap ,Xdiff
;
Parameter
         FinDem(R,S) Final demand, Amatrix(R,S,Rb,Sb) Technical coefficienties,
         ValueA(R,S) ValueAdded,
         Trade(R,Rb,S) Trade Table, VAshare(R,S) Value added share in production,
         Expshare(R,Rb,S) Export destination shares, TotExp(r,S), TotImp(r,S),
         ExpROW(R,S),ImpROW(R,S),
         Importshare(R,Rb,S) Import Origin shares, ImportshareDisImp(R,Rb,S) Local import shares,
         ImportratioPar(R,S) Import versus local production
         RealOutput(R,S),RealDemand(R,S),RealUse(R,S) ,RealDiff(R,S)
         Xbase(R,S),Xmarg(R,S) Marginal value on producing les,
         RatMarg(R,S) Marginal value on rationing
         TradeNew(rROW,rROWb,S) New trade matrix, TradeOrigin(rROWb,S),Tradedestination(rROWb,S),
         IDENT(R,S,Rb,Sb) identity ,
         AvaShare(R,S), IAmatrix(R,S,Rb,Sb), IAmatrix2(rsall,rsall),
         ReqMatrix2(rsall,rsall),
         wS(R,S) waste per sector, TotS(R,S), ValueAdded(R,S),WSshare(R,S),Rdem(R,S) Reconstruction demand,
         cost(R) ,
         Z_matrix(R,S,Rb,Sb)
         test(r,s)
         local_Z(R,S), LFD(R,S)  , Shock(R,S)    , Xdiff_dis(R,S)

;
VARIABLE
         Z objective, DisImp1(R,S) Disaster Additional Imports
;
POSITIVE VARIABLE
         X(R,S) total production , Demand(R,S) demand,  XP(R,S) total products, Rationdem(R,S) Rationed demand,
         DisImp(R,S) Disaster Additional Imports, DisImpNeg(R,S) Negative of Disaster Additional Imports;

* BASE DATA
FinDem(R,S) = sum((Rb,fdemand), FinDem_ini(R,S,Rb,fdemand))    ;
ExpROW(R,S) = ExpROW_ini(R,S,'Export');
X.L(R,S) = sum((Rb,Sb), Z_matrix_ini(R,S,Rb,Sb)) + FinDem(R,S) + ExpROW(R,S) ;

* A matrix
Amatrix(R,S,Rb,Sb) = A_matrix_ini(R,S,Rb,Sb);
Z_matrix(R,S,Rb,Sb) =  Amatrix(R,S,Rb,Sb)*X.L(Rb,Sb);

* Total use
Xbase(R,S) = sum((Rb,Sb), Amatrix(R,S,Rb,Sb)*X.L(Rb,Sb)) + FinDem(R,S) + ExpROW(R,S) ;

*Value Added
ValueA(R,S) = ValueA_ini(R,S,'VA') ;
VAShare(R,S)$Xbase(R,S) =  ValueA(R,S)$Xbase(R,S)/Xbase(R,S);

*Calculate locals
local_Z(R,S) = sum((Sb), Amatrix(R,S,R,Sb)*X.L(R,Sb))   ;
*sum(Sb,Z_matrix(R,S,R,Sb))     ;
LFD(R,S) = sum((fdemand), FinDem_ini(R,S,R,fdemand))  ;

*ADD TRADE
Trade(R,Rb,S)$(ord(Rb)<>ord(R))   = sum(Sb,Z_matrix(Rb,S,R,Sb))  +sum((fdemand), FinDem_ini(Rb,S,R,fdemand))   ;

*LOAD EXPORTS
TotExp(R,S)=sum((Rb), Trade(Rb,R,S));

* LOAD IMPORTS
TotImp(R,S)=sum((Rb), Trade(R,Rb,S));

Importshare(R,Rb,S)$(sum((Sb), Amatrix(R,S,Rb,Sb)*X.L(Rb,Sb)) + FinDem(Rb,S))=Trade(Rb,R,S)$(sum((Sb), Amatrix(R,S,Rb,Sb)*X.L(Rb,Sb)) + FinDem(Rb,S))/(sum((Sb), Amatrix(R,S,Rb,Sb)*X.L(Rb,Sb)) + FinDem(Rb,S));
ImportshareDisImp(Rb,R,S) = Importshare(R,Rb,S)           ;


execute_unload 'test.gdx' X,Xbase,TotExp,LFD,ExpROW,Importshare,Trade,FinDem


EQUATIONS
         demsup(R,S)             demand is equal to supply on the product level for every region
         Objective               The objective function
;

*PRE-DISASTER EQUATION:
demsup(R,S)..
       X(R,S)  =g=  (0
       + sum((Sb), Amatrix(R,S,R,Sb)*X(R,Sb)) + LFD(R,S)
       + sum(Rb$(ord(Rb)<>ord(R)), Importshare(R,Rb,S)*(sum((Sb), Amatrix(R,S,Rb,Sb)*X(Rb,Sb)) + FinDem(Rb,S)))
       + ExpROW(R,S)) ;
;

Objective..
Z =e=
*Production costs
     sum((R,S), X(R,S))
    ;

MODEL
         LPIO base supply and use model /demsup,Objective/;

Regmaxcap=0.98;
X.up(R,S)=1.05*(1/Regmaxcap)*X.L(R,S);

* This is the baseline situation, this should give a solutation where Xdiff (see below) should be close to zero.

option threads=0;
Option Reslim=10000;
option LP=conopt4;
*LPIO.OptFile = 1;
SOLVE LPIO minimizing Z using LP;

* CHECK IF DATA IS BALANCED
RealUse(R,S)  = sum((Sb), Amatrix(R,S,R,Sb)*X.L(R,Sb)) + LFD(R,S)
                 + sum(Rb$(ord(Rb)<>ord(R)), Importshare(R,Rb,S)*((sum((Sb), Amatrix(R,S,Rb,Sb)*X.L(Rb,Sb)) + FinDem(Rb,S))))
                 + ExpROW(R,S)
;


RealOutput(R,S) =   X.L(R,S);
RealDiff(R,S) = RealOutput(R,S) - RealUse(R,S);
test_diff =  sum((R,S),RealDiff(R,S));

Xdiff = sum((R,S),Xbase(R,S) - X.L(R,S));


execute_unload 'output_TheVale_1.gdx' Demand, Xdiff, X ,RealDiff , ImportratioPar, DisImp,RationDem;

EQUATIONS
         demDisRatMarg(R,S)      demand is equal to supply on the product level for every region
         ObjectiveMarg           The objective function
;


*POST-DISASTER EQUATION with demand rationing:
demDisRatMarg(R,S)..
       DisImp(R,S) + X(R,S)  =g= 0
                 + sum((Sb), Amatrix(R,S,R,Sb)*X(R,Sb)) + LFD(R,S) - Rationdem(R,S) + Rdem(R,S)
                 + sum(Rb$(ord(Rb)<>ord(R)), Importshare(R,Rb,S)*((sum((Sb), Amatrix(R,S,Rb,Sb)*X(Rb,Sb)) - Rationdem(Rb,S) + FinDem(Rb,S) + (Rdem(Rb,S)))))
                 + sum(Rb$(ord(Rb)<>ord(R)), Importshare(R,Rb,S)*(DisImp(Rb,S)))
                 + ExpROW(R,S)
;

ObjectiveMarg..
Z =e=
*Production costs
     sum((R,S), (X(R,S)))
*Niet gratis uit de rest van de wereld:
     + sum((R,S),
       sum(Rb$(ord(Rb)<>ord(R)), Importshare(R,Rb,S)*((sum((Sb), Amatrix(R,S,Rb,Sb)*X.L(Rb,Sb)) - Rationdem(Rb,S) + FinDem(Rb,S)  + (Rdem(Rb,S)))))
     + sum(Rb$(ord(Rb)<>ord(R)), Importshare(R,Rb,S)*(DisImp(Rb,S)))
        )
  ;

* DEFINE MODELS TO SOLVE:

MODEL
         LPIODisMarg supply and use model with endogenous imports but no maximum function /demDisRatMarg,ObjectiveMarg/;


LPIODISMarg.solvelink=5;
LPIODisMarg.workfactor=1.5 ;


Regmaxcap=0.98;
X.up(R,S)=1.10*(1/Regmaxcap)*Xbase(R,S)+1;
Rationdem.fx(R,S)=0;
Rdem(R,S) = 0;
DisImp.fx(R,S)=0;
*option LP=osimosek;
LPIODisMarg.OptFile = 1;
*SOLVE LPIODisMarg minimizing Z using LP;
Xmarg(R,S)=X.M(R,S);
option NLP=ipopt;
LPIODisMarg.OptFile = 1;
SOLVE LPIODisMarg minimizing Z using LP;
Xmarg(R,S)=X.M(R,S);
Ratmarg(R,S)=abs(Rationdem.M(R,S));
Ratmarg(R,S)$(Ratmarg(R,S)<1)=1;
*Ratmarg(R,S) = 9;
display Xmarg,Ratmarg;
