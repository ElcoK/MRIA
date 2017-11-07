# Multiregional Impact Assessment Library (mria_py)

Python implementation of a multiregional impact assessment model, to be used with various input-output and supply-use data sources. 


**Requirements:** [NumPy](http://www.numpy.org/), [Pyomo](http://www.pyomo.org/), [IPOPT](https://projects.coin-or.org/Ipopt), [pandas](https://pandas.pydata.org/), [geopandas](http://geopandas.org/), [seaborn](https://seaborn.pydata.org/), [matplotlib](https://matplotlib.org/)

**Core Paper:** [Koks and Thissen 2016](http://www.tandfonline.com/doi/full/10.1080/09535314.2016.1232701)

```
Koks, E. E., & Thissen, M. (2016). A multiregional impact assessment model for disaster analysis. 
  Economic Systems Research, 28(4), 429-449.
```

**Other applications:**
* Regional disaster impact analysis: comparing input–output and computable general equilibrium models ([Koks et al. 2016](https://www.nat-hazards-earth-syst-sci.net/16/1911/2016/))
* Economic Impacts of Irrigation-Constrained Agriculture in the Lower Po Basin ([Pérez-Blanco et al. 2017](http://www.worldscientific.com/doi/abs/10.1142/S2382624X17500035))

### Work in progress:
* Add compatibility with more openly available MRIO and IRIO data sources.
* Improve uncertainty and sensitivity analysis of the model.
* Create additional IPython Notebooks with examples.
* Make it an actual python package.

### License
Copyright (C) 2017 Elco Koks. All versions released under the [MIT license](LICENSE.md).
