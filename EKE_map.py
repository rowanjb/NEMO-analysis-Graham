#simple throwaway script making maps of data 
  
import xarray as xr
import LSmap
import numpy as np
import math

def eke_map(mask, run1, run2=False):
    
    for depth in ['50','200','1000','2000']:

        path1 = run1 + '_EKE/' + run1 + '_EKE_map_' + mask + depth + '.nc'
        da1 = xr.open_dataarray(path1)
        da1 = da1.where(da1 > 0)

        if run2!=False:
            path2 = run2 + '_EKE/' + run2 + '_EKE_map_' + mask + depth + '.nc'
            da2 = xr.open_dataarray(path2)
            da2 = da2.where(da2 > 0)
            da = da1-da2
        else:
            da = da1

        minmax = LSmap.xrLSminmax(da,da.nav_lat_grid_T,da.nav_lon_grid_T)

        if run2!=False:
            CBlabel = '$\Delta$EKE ($J$)'
        else:
            CBlabel = 'EKE ($J$)'

        if mask == 'LS2k': mask_description = ' interior'
        elif mask == 'LS': mask_description = ''
        elif mask == 'LSCR': mask_description = ' convection region'

        if run2!=False:
            title = 'Difference in eddy kinetic energy in the top ' + depth + 'm of \nthe Labrador Sea' + mask_description + ', ' + run1 + '-' + run2
            fileName  = 'pics_EKE/' + run1 + '-' + run2 + '_EKE_map_' + mask + depth
        else:
            title = 'Eddy kinetic energy in the top ' + depth + 'm of \nthe Labrador Sea' + mask_description + ', ' + run1
            fileName  = 'pics_EKE/' + run1 + '_EKE_map_' + mask + depth

        LSmap.LSmap(da,da.nav_lon_grid_T,da.nav_lat_grid_T,minmax,CBlabel,title,fileName)#,scale='log')

if __name__ == "__main__":
    eke_map(mask='LS', run1='EPM151', run2='EPM155')
    eke_map(mask='LS', run1='EPM151', run2='EPM157')
    eke_map(mask='LS', run1='EPM155', run2='EPM157')
    eke_map(mask='LS', run1='EPM152', run2='EPM156')
    eke_map(mask='LS', run1='EPM152', run2='EPM158')
    eke_map(mask='LS', run1='EPM156', run2='EPM158')

