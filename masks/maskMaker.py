#simple little script for making masks
#these masks are full-depth, i.e., they have a depth-dimensions

import xarray as xr
import numpy as np

#using a random ANHA4 file as a basis for making the masks
filepath = '/home/rowan/projects/rrg-pmyers-ad/pmyers/ANHA4/ANHA4-EPM151-S/ANHA4-EPM151_y2002m05d10_gridT.nc'
testFile = xr.open_dataset(filepath)

###################################################################################################################################################
#MASKING WHERE LABRADOR SEA DEPTH IS LESS THAN 2000m
###################################################################################################################################################

exact_depth = testFile.deptht.sel(deptht=2000,method="nearest") #getting the depth of the nearest layer to 2000m
testFile = testFile.isel(time_counter=0) #basically getting rid of a dimension
vosaline = testFile.vosaline #just looking at vosaline; where salinity=0 we have land, and where salinity!=0 we have water
vosaline = vosaline.where(vosaline > 0) #getting rid of values in land, where salinity=0

#only looking at the lab sea
northLat = 66
westLon = -65
southLat = 53
eastLon = -43
vosaline = vosaline.where(vosaline.nav_lat_grid_T < northLat)
vosaline = vosaline.where(vosaline.nav_lon_grid_T < eastLon)
vosaline = vosaline.where(vosaline.nav_lat_grid_T > southLat)
vosaline = vosaline.where(vosaline.nav_lon_grid_T > westLon)

#getting the 2000m mask 
vosaline = vosaline.where(vosaline > 0) #getting rid of values in land, where salinity=0
exact_depth_slice = vosaline.where(vosaline.deptht == exact_depth, drop=True) #getting a single layer at the deptht nearest 2000 m
exact_depth_slice = exact_depth_slice.isel(deptht=0) #basically getting rid of a dimension 
exact_depth_slice = exact_depth_slice.notnull() #looking at where there are values and where there aren't (because we made shelves/land=NaN earlier)
mask, vosaline = xr.broadcast(exact_depth_slice, vosaline) #getting the slice into the right shape (basically so there are ~50 depth slices instead of 1)
mask = mask.drop_vars(['time_centered','time_counter']) #dropping coordinates
mask.attrs = {'description': 'ANHA4 mask of Labrador Sea wherever the depth is greater than 2000 m'} #add descriptive attribute
mask = mask.rename('mask_LS_2k') #renaming the dataarray
mask.to_netcdf('mask_LS_2k.nc') #saving the mask

###################################################################################################################################################
#MASKING THE ENTIRE LABRADOR SEA
###################################################################################################################################################

#getting mask of LS region, disregarding land and outside of bounds in the above section
maskLS = vosaline.notnull() #convert to bool, basically (note that shelves are masked)
maskLS = maskLS.rename('mask_LS') #rename from vosaline
maskLS = maskLS.drop_vars(['time_centered','time_counter']) #remove coordinates
maskLS.attrs = {'description': 'ANHA4 mask of Labrador Sea between 53N & 66N and 43W & 65W'} #add descriptive attribute 
maskLS.to_netcdf('mask_LS.nc') #saving the mask

###################################################################################################################################################
#MASKING THE NORTH-WEST ATLANTIC (basically the same as the LS mask but a bit bigger)
###################################################################################################################################################

#only looking at the lab sea
northLat = 70
westLon = -70
southLat = 50
eastLon = -40
vosaline = testFile.vosaline #getting vosaline again 
vosaline = vosaline.where(vosaline > 0) #getting rid of values in land, where salinity=0
vosaline = vosaline.where(vosaline.nav_lat_grid_T < northLat)
vosaline = vosaline.where(vosaline.nav_lon_grid_T < eastLon)
vosaline = vosaline.where(vosaline.nav_lat_grid_T > southLat)
vosaline = vosaline.where(vosaline.nav_lon_grid_T > westLon)

#getting mask of (the bigger) LS region, disregarding land
maskLS = vosaline.notnull() #convert to bool, basically
maskLS = maskLS.rename('mask_LS_bigger') #rename from vosaline
maskLS = maskLS.drop_vars(['time_centered','time_counter']) #remove coordinates
maskLS.attrs = {'description': 'ANHA4 mask of Labrador Sea between 50N & 70N and 40W & 70W'} #add descriptive attribute
maskLS.to_netcdf('mask_LS_bigger.nc') #saving the mask
