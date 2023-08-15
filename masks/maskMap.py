#simple throwaway script for making maps of masks

import xarray as xr
import maskLSmap2
import numpy as np 

mask_path = 'ARGOProfiles_mask.nc'

if mask_path == 'ARGOProfiles_mask.nc':
    mask = xr.open_dataset(mask_path)#.astype(int)
    mask = mask.isel(n=0)
    mask = mask.tmask
    with xr.open_dataset('ANHA4_mesh_mask.nc') as DS:
        lons = np.array(DS.variables['nav_lon'])
        lats = np.array(DS.variables['nav_lat']) 
    mask = mask.assign_coords({'nav_lon_grid_T':(['y','x'],lons),'nav_lat_grid_T':(['y','x'],lats)})
else:
    mask = xr.open_dataarray(mask_path)#.astype(int)
    mask = mask.isel(deptht=0)

#print(mask)
#mask = xr.open_dataarray('mask_LS.nc')#.astype(int)
#mask = mask.isel(deptht=0)

fileName  = 'mask_LSCR'
#maskLSmap.LSmap(mask.tmask.astype(int),lons,lats,(0,1),CBlabel,title,fileName) #if you're looking at LSCR
maskLSmap2.LSmap(mask,(0,1),fileName) #if you're looking at LS2k or LS


