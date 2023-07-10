#Produces current velocity in the top 50 m 
#Rowan Brown
#17 May 2023

#outputs netcdf files
# - 4 x depths (50m, 200m, 1000m, 2000m)
# - 2 x parameters (heat content and average temperatures)
# - 3 x masks
# - 2 x output data "formats":
#   - HC/temperature in each column averaged across time, for mapping purposes (should this be updated so that the window can be spec'ed?) 
#   - total HC/average temperature in the masked region, for plotting in time

import numpy as np 
import pandas as pd
import xarray as xr
import os

#user specs
run = 'EPM158' #specify the run
mask_choice = 'LSCR' #choose which mask; options are 'LSCR', 'LS2k', or 'LS'

#creating directory if doesn't already exist
dir = run + '_heat/'
if not os.path.exists(dir):
    os.makedirs(dir)

##################################################################################################################
#MASKS

#mask for land, bathymetry, etc. and horiz. grid dimensions
with xr.open_dataset('masks/ANHA4_mesh_mask.nc') as DS:
    tmask = DS.tmask[0,:,:,:].rename({'z': 'deptht', 'y': 'y_grid_T', 'x': 'x_grid_T'}) #DataArray with dims (t: 1, z: 50, y: 800, x: 544) 
    e1t = DS.e1t[0,:,:].rename({'y': 'y_grid_T', 'x': 'x_grid_T'})
    e2t = DS.e2t[0,:,:].rename({'y': 'y_grid_T', 'x': 'x_grid_T'})

if mask_choice == 'LS2k': #mask for 2000m depth interior area
    mask = xr.open_dataarray('masks/mask_LS_2k.nc').astype(int)
elif mask_choice == 'LS': #mask for entire LS region
    mask = xr.open_dataarray('masks/mask_LS.nc').astype(int)
elif mask_choice == 'LSCR': #mask for LS convection region
    mask = xr.open_dataset('masks/ARGOProfiles_mask.nc').tmask.astype(int).rename({'x':'x_grid_T','y':'y_grid_T'})
else: 
    print("Y'all didn't choose a mask")
    quit()

#################################################################################################################
#OPENING AND INITIAL PROCESSING OF THE NETCDF MODEL OUTPUT FILES

#these are text files with lists of all non-empty model outputs (made with 'filepaths.py')
gridU_txt = run + '_filepaths/' + run + '_gridU_filepaths.txt'
gridV_txt = run + '_filepaths/' + run + '_gridV_filepaths.txt'
gridT_txt = run + '_filepaths/' + run + '_gridT_filepaths.txt'

#open the text files and get lists of the .nc output filepaths
with open(gridU_txt) as f: lines = f.readlines()
filepaths_gridU = [line.strip() for line in lines][:3]
with open(gridV_txt) as f: lines = f.readlines()
filepaths_gridV = [line.strip() for line in lines][:3]
with open(gridT_txt) as f: lines = f.readlines()
filepaths_gridT = [line.strip() for line in lines][:3]

#preprocessing (specifying variables that we need and ignoring the rest)
preprocess_gridU = lambda ds: ds[['e3u','vozocrtx']]
preprocess_gridV = lambda ds: ds[['e3v','vomecrty']]
preprocess_gridT = lambda ds: ds[['e3t']]

#open the datasets
DSU = xr.open_mfdataset(filepaths_gridU,preprocess=preprocess_gridU,engine="netcdf4")
DSV = xr.open_mfdataset(filepaths_gridV,preprocess=preprocess_gridV,engine="netcdf4")
DST = xr.open_mfdataset(filepaths_gridT,preprocess=preprocess_gridT,engine="netcdf4")

#renaming dimensions so that they are the same for all datasets
DSU = DSU.rename({'depthu': 'z', 'y': 'y_grid_T', 'x': 'x_grid_T'})
DSV = DSV.rename({'depthv': 'z', 'y': 'y_grid_T', 'x': 'x_grid_T'})
DST = DST.rename({'deptht': 'z'})

#add horizontal cell dimensions as variables 
DST = DST.assign(e1t=e1t,e2t=e2t)

#apply tmask (i.e., masking bathy)
DSU = DSU.where(tmask == 1)
DSV = DSV.where(tmask == 1)
DST = DST.where(tmask == 1)

##apply mask (if there is one)
#if mask_choice == 'LSCR' or mask_choice == 'LS2k' or mask_choice == 'LS':
#    DSV.coords['mask'] = mask
#    DSV = DSV.where(DSV.mask == 1, drop=True)
#    DSU.coords['mask'] = mask
#    DSU = DSU.where(DSU.mask == 1, drop=True)
#    DST.coords['mask'] = mask
#    DST = DST.where(DST.mask == 1, drop=True)

##################################################################################################################
#CALCULATIONS

#first, velocities are co-located on the T grid:
DSU = DSU.interp(x_grid_T = DSU.x_grid_T + 0.5) #shifting "right"
DSV = DSV.interp(y_grid_T = DSV.y_grid_T - 0.5) #shifting "down"

#re-mapping 'x' and 'y' so they're consistent with the T grid
DSU = DSU.assign_coords(x_grid_T = DSU.x_grid_T - 0.5)
DSV = DSV.assign_coords(y_grid_T = DSV.y_grid_T + 0.5)

#adding velocities to the T-grid
DST.coords['U'] = DSU.vozocrtx
DST.coords['V'] = DSV.vomecrty
DST = DST.drop_vars(['nav_lat','nav_lon'])

#apply mask (if there is one)
if mask_choice == 'LSCR' or mask_choice == 'LS2k' or mask_choice == 'LS':
    DST.coords['mask'] = mask
    DST = DST.where(DST.mask == 1, drop=True)

#loop through the 4 depths and save .nc files
for d in [50, 200, 1000, 2000]: #loop through depths
    DS_d = DST.where(DST.deptht < d, drop=True) #drop values below specified depth






##############you're here






    #note: there are two main ideas below: "col" refers to the idea that we're looking at water-columnwise averages, ie so we can make maps later. On 
    #the other hand, "region" refers to regionwise averages, so that we can make time plots later.

    #masking shelves
    #NOTE: bathy is masked to avoid skewed understandings/results from the on-shelf values this section could be commented out if needed 
    bottom_slice = DS_d.votemper.isel(deptht = -1).isel(time_counter = 0) 
    bottom_slice_bool = bottom_slice.notnull()
    shelf_mask, temp = xr.broadcast(bottom_slice_bool, DS_d.votemper.isel(time_counter=0))
    DS_d = DS_d.where(shelf_mask) 

    #temperature averaged through time 
    #cell weights (col): divide cell volume by average cell volume in each column
    volumes = DS_d.e1t*DS_d.e3t*DS_d.e2t #volume of each cell
    avg_col_vol = volumes.mean(dim='deptht') #average cell volume in each column 
    weights = volumes/avg_col_vol #dataarray of weights 
    weights = weights.fillna(0)
    votemper_col_weighted = DS_d.votemper.weighted(weights)
    votemper_avg_col = votemper_col_weighted.mean(dim='deptht') #NOTE: skipna should be True if not blocking shelves
    votemper_avg_col_time = votemper_avg_col.mean(dim='time_counter')
    votemper_avg_col_time.to_netcdf(run + '_heat/' + run + '_votemper_timeAvg_' + mask_choice + str(d) + '.nc') #.nc with time-avg temp in each column (ie for making maps)

    #temperature averaged in space
    #cell weights (region): divide cell volume by average cell volume in the whole masked region
    avg_cell_vol = volumes.mean(dim=['deptht','y_grid_T','x_grid_T'])
    weights = volumes/avg_cell_vol
    weights = weights.fillna(0)
    votemper_region_weighted = DS_d.votemper.weighted(weights)
    votemper_avg_region = votemper_region_weighted.mean(dim=['deptht','y_grid_T','x_grid_T'],skipna=True)
    votemper_avg_region.to_netcdf(run + '_heat/' + run + '_votemper_spaceAvg_' + mask_choice + str(d) + '.nc') 

    #heat content
    HC = rho_0 * C_p * 10**(-12) * (DS_d.votemper - refT) * volumes  
    HC_sum_deptht = HC.sum(dim='deptht')
    HC_avg_time = HC_sum_deptht.mean(dim='time_counter')
    HC_avg_time.to_netcdf(run + '_heat/' + run + '_HC_timeAvg_' + mask_choice + str(d) + '.nc') 
    HC_sum_space = HC_sum_deptht.sum(dim=['y_grid_T','x_grid_T'])
    HC_sum_space.to_netcdf(run + '_heat/' + run + '_HC_spaceSum_' + mask_choice + str(d) + '.nc')