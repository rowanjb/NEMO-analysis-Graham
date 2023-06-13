#simple throwaway script making maps of data 

import xarray as xr
import LSmap 
import numpy as np 

path = 'EPM151_EKE/EPM151_EKE_timeAvg_LS50.nc'
EKE = xr.open_dataarray(path)

minmax = LSmap.xrLSminmax(EKE,EKE.nav_lat_grid_T,EKE.nav_lon_grid_T)

CBlabel = 'EKE ($J$)'
title = 'Test map of EKE in LS'
fileName  = 'test_map_EKE'
LSmap.LSmap(EKE,EKE.nav_lon_grid_T,EKE.nav_lat_grid_T,minmax,CBlabel,title,fileName,scale='log')


