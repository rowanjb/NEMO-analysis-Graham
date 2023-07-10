#simple throwaway script making maps of data 

import xarray as xr
import LSmap 
import numpy as np 
import math

variable = 'avg_MLD' #max_MLD or avg_MLD
mask = 'LS' #LS or LSCR or LS2k, though if you plot LS it captures LSCR and LS2k anyway...
run1 = 'EPM156'
run2 = 'EPM158'

path1 = run1 + '_MLD/' + run1 + '_' + variable + '_map_' + mask + '.nc'
da1 = xr.open_dataarray(path1)

path2 = run2 + '_MLD/' + run2 + '_' + variable + '_map_' + mask + '.nc'
da2 = xr.open_dataarray(path2)

##dealing within masked areas where FWC=0
#if variable=='FWC':
#    da1 = da1.where(da1 != 0)
#    da2 = da2.where(da2 != 0)

da = da1-da2    
minmax = LSmap.xrLSminmax(da,da.nav_lat_grid_T,da.nav_lon_grid_T)
#mn = math.floor(minmax[0]*4)/4
#mx = math.ceil(minmax[1]*4)/4
#minmax = mn,mx

CBlabel = 'MLD depth ($m$)'

if mask == 'LS2k': mask_description = ' interior'
elif mask == 'LS': mask_description = ''
elif mask == 'LSCR': mask_description = ' convection region'
    
if variable=='max_MLD': title = 'Difference of the max mixed layer depth in \nthe Labrador Sea' + mask_description + ', ' + run1 + '-' + run2
if variable=='avg_MLD': title = 'Difference of the  average mixed layer depth in \nthe Labrador Sea' + mask_description + ', ' + run1 + '-' + run2

fileName  = 'pics_MLD/' + run1 + '-' + run2 + '_' + variable + '_map_' + mask
LSmap.LSmap(da,da.nav_lon_grid_T,da.nav_lat_grid_T,minmax,CBlabel,title,fileName)#,scale='log')

