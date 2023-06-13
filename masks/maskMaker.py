#simple little script for making masks

import xarray as xr
import numpy as np

filepath = '/home/rowan/projects/rrg-pmyers-ad/pmyers/ANHA4/ANHA4-EPM151-S/ANHA4-EPM151_y2002m05d10_gridT.nc'
testFile = xr.open_dataset(filepath)

northLat = 66
westLon = -65
southLat = 53
eastLon = -43

#add the shelves masking here!!!???

exact_depth = testFile.deptht.sel(deptht=2000,method="nearest")
#testFile = testFile.where(testFile.deptht <= exact_depth) #keep only data above 2000 m
testFile = testFile.isel(time_counter=0) #basically getting rid of a dim
vosaline = testFile.vosaline #just looking at vosaline (to save memory)
vosaline = vosaline.where(vosaline > 0) #getting rid of values in land, where salinity=0

#only looking at the lab sea
vosaline = vosaline.where(vosaline.nav_lat_grid_T < northLat)
vosaline = vosaline.where(vosaline.nav_lon_grid_T < eastLon)
vosaline = vosaline.where(vosaline.nav_lat_grid_T > southLat)
vosaline = vosaline.where(vosaline.nav_lon_grid_T > westLon)

#getting mask of LS region, disregarding land and outside of above bounds
maskLS = vosaline.notnull() #convert to bool, basically
maskLS = maskLS.rename('mask_LS') #rename from vosaline
maskLS = maskLS.drop_vars(['time_centered','time_counter'])
maskLS.attrs = {'description': 'ANHA4 mask of Labrador Sea between 53N & 66N and 43W & 65W'}
maskLS.to_netcdf('mask_LS.nc')

#getting mask only where depth is greater than 2000 m
vosaline = vosaline.where(vosaline > 0) #getting rid of values in land, where salinity=0
exact_depth_slice = vosaline.where(vosaline.deptht == exact_depth, drop=True) #getting single layer at deptht nearest 2000 m
exact_depth_slice = exact_depth_slice.isel(deptht=0) #basically getting rid of a dim
exact_depth_slice = exact_depth_slice.notnull() #looking at where there are values and where there aren't (shelves/land is NaN)
mask, vosaline = xr.broadcast(exact_depth_slice, vosaline) #getting the slice into the right shape (basically so there are 50 depth slices)
#mask = mask.where(mask.deptht <= exact_depth) #keep only data above 2000 m
mask = mask.drop_vars(['time_centered','time_counter'])
mask.attrs = {'description': 'ANHA4 mask of Labrador Sea wherever the depth is greater than 2000 m'}
mask = mask.rename('mask_LS_2k')
mask.to_netcdf('mask_LS_2k.nc')

