#simple throwaway script making maps of data 

import xarray as xr
import LSmap 
import numpy as np 
import math

def convr_map(mask, run1, run2=False):

    for depth in ['50','200','1000','2000']:

        path1 = run1 + '_convR/' + run1 + '_convR_map_' + mask + depth + '.nc'
        da1 = xr.open_dataarray(path1)
        
        if run2!=False:
            path2 = run2 + '_convR/' + run2 + '_convR_map_' + mask + depth + '.nc'
            da2 = xr.open_dataarray(path2)
            da = da1-da2
        else:
            da = da1

        minmax = LSmap.xrLSminmax(da,da.nav_lat_grid_T,da.nav_lon_grid_T)
        #mn = math.floor(minmax[0])
        #mx = math.ceil(minmax[1])
        #minmax = mn,mx

        CBlabel = 'Convective resistance ($J$ $m^{-3}$)'

        if mask == 'LS2k': mask_description = ' interior'
        elif mask == 'LS': mask_description = ''
        elif mask == 'LSCR': mask_description = ' convection region'
        
        if run2!=False:
            title = 'Difference in convective resistance in the top ' + depth + 'm of \nthe Labrador Sea' + mask_description + ', ' + run1 + '-' + run2
            fileName  = 'pics_convR/' + run1 + '-' + run2 + '_convR_map_' + mask + depth
        else:
            title = 'Convective resistance in the top ' + depth + 'm of \nthe Labrador Sea' + mask_description + ', ' + run1
            fileName  = 'pics_convR/' + run1 + '_convR_map_' + mask + depth

        LSmap.LSmap(da,da.nav_lon_grid_T,da.nav_lat_grid_T,minmax,CBlabel,title,fileName)#,scale='log')

if __name__ == "__main__":
    convr_map(mask='LS', run1='EPM151')
    convr_map(mask='LS', run1='EPM152')
    convr_map(mask='LS', run1='EPM155')
    convr_map(mask='LS', run1='EPM156')
    convr_map(mask='LS', run1='EPM157')
    convr_map(mask='LS', run1='EPM158')
