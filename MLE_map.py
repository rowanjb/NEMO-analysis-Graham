#simple throwaway script making maps of data 

import xarray as xr
import LSmap 
import numpy as np 
import math

def mle_map(mask, run1, run2=False):
    
    #EPM158_MLE_Q_map_MASKCHOICE.NC
    #Q.map.to_netcdf(run + '_MLE/' + run + '_MLE_Q_map_' + mask + '.nc')

    path1 = run1 + '_MLE/' + run1 + '_MLE_Q_map_' + mask + '.nc'
    da1 = xr.open_dataarray(path1)

    if run2!=False:
        path2 = run2 + '_MLD/' + run2 + '_' + variable + '_map_' + mask + '.nc'
        da2 = xr.open_dataarray(path2)
        da = da1-da2    
    else:
        da = da1

    minmax = LSmap.xrLSminmax(da,da.nav_lat_grid_T,da.nav_lon_grid_T)

    CBlabel = 'Heat flux ($J/S$?)'

    if run2!=False:
        title = 'Difference of the average mixed layer depth in \nthe Labrador Sea, ' + run1 + '-' + run2
        fileName  = 'pics_MLD/' + run1 + '-' + run2 + '_' + variable + '_map_' + mask
    else:
        title = 'Average heat flux through the bottom of the mixed layer, ' + run1 
        fileName  = 'pics_MLE/' + run1 + '_MLE_Q_map'
    
    LSmap.LSmap(da,da.nav_lon_grid_T,da.nav_lat_grid_T,(0,150),CBlabel,title,fileName)#,scale='log')

if __name__ == "__main__":
    mle_map(mask='LS', run1='EPM158')
    #mld_map(variable='avg_MLD', mask='LS', run1='EPM158')
    #mld_map(variable='max_MLD', mask='LS', run1='EPM158')
