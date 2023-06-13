#simple throwaway script for making maps of masks

import xarray as xr
import LSmap 
import numpy as np 

mask_path = 'mask_LS_2k.nc'
mask = xr.open_dataarray(mask_path)
with xr.open_dataset('ANHA4_mesh_mask.nc') as DS:
    lons = np.array(DS.variables['nav_lon'])
    lats = np.array(DS.variables['nav_lat'])


CBlabel = 'Maskiness'
title = 'Mask of LS with depth > 2000'
fileName  = 'maskLS_2k'
LSmap.LSmap(mask.isel(deptht=0),mask.nav_lon_grid_T,mask.nav_lat_grid_T,(0,1),CBlabel,title,fileName)


