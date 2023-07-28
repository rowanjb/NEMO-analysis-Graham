#simple throwaway script making maps of data 

import xarray as xr
import LSmap 
import numpy as np 
import math

def mld_map(variable, mask, run1, run2=False):
    
    path1 = run1 + '_MLD/' + run1 + '_' + variable + '_map_' + mask + '.nc'
    da1 = xr.open_dataarray(path1)

    if run2!=False:
        path2 = run2 + '_MLD/' + run2 + '_' + variable + '_map_' + mask + '.nc'
        da2 = xr.open_dataarray(path2)
        da = da1-da2    
    else:
        da = da1

    minmax = LSmap.xrLSminmax(da,da.nav_lat_grid_T,da.nav_lon_grid_T)

    CBlabel = 'MLD depth ($m$)'

    if run2!=False:
        if variable=='max_MLD': title = 'Difference of the max mixed layer depth in \nthe Labrador Sea, ' + run1 + '-' + run2
        if variable=='avg_MLD': title = 'Difference of the average mixed layer depth in \nthe Labrador Sea, ' + run1 + '-' + run2
        fileName  = 'pics_MLD/' + run1 + '-' + run2 + '_' + variable + '_map_' + mask
    else:
        if variable=='max_MLD': title = 'Max mixed layer depth in the Labrador Sea, ' + run1 
        if variable=='avg_MLD': title = 'Average mixed layer depth in the Labrador Sea, ' + run1 
        fileName  = 'pics_MLD/' + run1 + '_' + variable + '_map_' + mask
    
    LSmap.LSmap(da,da.nav_lon_grid_T,da.nav_lat_grid_T,minmax,CBlabel,title,fileName)#,scale='log')

if __name__ == "__main__":
    mld_map(variable='avg_MLD', mask='LS', run1='EPM158')
    mld_map(variable='max_MLD', mask='LS', run1='EPM158')
