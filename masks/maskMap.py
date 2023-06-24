#simple throwaway script for making maps of masks

import xarray as xr
import maskLSmap
import numpy as np 

#mask_path = 'ARGOProfiles_mask.nc' #'mask_LS_2k.nc'
mask_path = 'mask_LS.nc'
mask = xr.open_dataarray(mask_path)#.astype(int)
with xr.open_dataset('ANHA4_mesh_mask.nc') as DS:
    lons = np.array(DS.variables['nav_lon'])
    lats = np.array(DS.variables['nav_lat'])

CBlabel = 'Maskiness'
title = 'Mask of LS with depth > 2000'
fileName  = 'mask_LS'
#maskLSmap.LSmap(mask.tmask.astype(int),lons,lats,(0,1),CBlabel,title,fileName) #if you're looking at LSCR
maskLSmap.LSmap(mask.isel(deptht=0),mask.nav_lon_grid_T,mask.nav_lat_grid_T,(0,1),CBlabel,title,fileName) #if you're looking at LS2k or LS


