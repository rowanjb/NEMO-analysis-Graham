#simple throwaway script making maps of data 

import xarray as xr
import LSmap 
import numpy as np 
import math


def salt_map(difference_plot, variable, mask, run1, run2):

    for depth in ['50','200','1000','2000']:

        path1 = run1 + '_salt/' + run1 + '_' + variable + '_timeAvg_' + mask + depth + '.nc'
        da1 = xr.open_dataarray(path1)

        if difference_plot:
            path2 = run2 + '_salt/' + run2 + '_' + variable + '_timeAvg_' + mask + depth + '.nc'
            da2 = xr.open_dataarray(path2)

        #dealing within masked areas where FWC=0
        if variable=='FWC':
            da1 = da1.where(da1 != 0)
            if difference_plot:
                da2 = da2.where(da2 != 0)

        if difference_plot:
            da = da1-da2 
        else:
            da = da1
        
        minmax = LSmap.xrLSminmax(da,da.nav_lat_grid_T,da.nav_lon_grid_T)

        if difference_plot:
            if variable=='vosaline': CBlabel = '$\Delta$S ($PSU$)'
            if variable=='FWC': CBlabel = '$\Delta$FWC ($m^3$)'
        else:
            if variable=='vosaline': CBlabel = 'S ($PSU$)'
            if variable=='FWC': CBlabel = 'FWC ($m^3$)'

       
        if mask == 'LS2k': mask_description = ' interior'
        elif mask == 'LS': mask_description = ''
        elif mask == 'LSCR': mask_description = ' convection region'
        
        if difference_plot:
            if variable=='vosaline': title = 'Difference in average salinity in the top ' + depth + 'm of \nthe Labrador Sea' + mask_description + ', ' + run1 + '-' + run2
            if variable=='FWC': title = 'Difference in freshwater content in the top ' + depth + 'm of \nthe Labrador Sea' + mask_description + ', ' + run1 + '-' + run2
            fileName  = 'pics_salt/' + run1 + '-' + run2 + '_' + variable + '_map_' + mask + depth
        else:
            if variable=='vosaline': title = 'Average salinity in the top ' + depth + 'm of \nthe Labrador Sea' + mask_description + ', ' + run1
            if variable=='FWC': title = 'Freshwater content in the top ' + depth + 'm of \nthe Labrador Sea' + mask_description + ', ' + run1
            fileName  = 'pics_salt/' + run1 + '_' + variable + '_map_' + mask + depth

        LSmap.LSmap(da,da.nav_lon_grid_T,da.nav_lat_grid_T,minmax,CBlabel,title,fileName)#,scale='log')

if __name__ == "__main__":
    difference_plot = False #if false, just plots the first run
    variable = 'vosaline' #vosaline or FWC
    mask = 'LS' #LS or LSCR or LS2k, though if you plot LS it captures LSCR and LS2k anyway...
    run1 = 'EPM158'
    run2 = 'EPM158'
    salt_map(difference_plot, 'vosaline', mask, run1, run2)
    salt_map(difference_plot, 'FWC', mask, run1, run2)
