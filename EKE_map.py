#simple throwaway script making maps of data 
  
import xarray as xr
import LSmap
import numpy as np
import math

mask = 'LS' #LS or LSCR or LS2k, though if you plot LS it captures LSCR and LS2k anyway...
run1 = 'EPM151'
run2 = 'EPM152'

for depth in ['50','200','1000','2000']:

    path1 = run1 + '_EKE/' + run1 + '_EKE_map_' + mask + depth + '.nc'
    da1 = xr.open_dataarray(path1)

    path2 = run2 + '_EKE/' + run2 + '_EKE_map_' + mask + depth + '.nc'
    da2 = xr.open_dataarray(path2)

    da1 = da1.where(da1 > 0)
    da2 = da2.where(da2 > 0)
    da = da1-da2


    minmax = LSmap.xrLSminmax(da,da.nav_lat_grid_T,da.nav_lon_grid_T)

    CBlabel = 'EKE ($J$)'

    if mask == 'LS2k': mask_description = ' interior'
    elif mask == 'LS': mask_description = ''
    elif mask == 'LSCR': mask_description = ' convection region'

    title = 'Difference in eddy kinetic energy in the top ' + depth + 'm of \nthe Labrador Sea' + mask_description + ', ' + run1 + '-' + run2

    fileName  = 'pics_EKE/' + run1 + '-' + run2 + '_EKE_map_' + mask + depth
    LSmap.LSmap(da,da.nav_lon_grid_T,da.nav_lat_grid_T,minmax,CBlabel,title,fileName)#,scale='log')


quit()
