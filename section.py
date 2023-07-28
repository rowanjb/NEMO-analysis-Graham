import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

import metpy.calc as mpcalc
from metpy.cbook import get_test_data
from metpy.interpolate import cross_section

run = 'EPM158'
gridT_txt = run + '_filepaths/' + run + '_gridT_filepaths.txt'
with open(gridT_txt) as f: lines = f.readlines()
filepaths_gridT = [line.strip() for line in lines][0]
ds = xr.open_dataset(filepaths_gridT)
ds = ds.rename({'deptht':'z','x_grid_T':'x','y_grid_T':'y','nav_lat_grid_T':'lat','nav_lon_grid_T':'lon'})
#ds = ds.assign_coords({'x':ds.x,'y':ds.y})
da = ds.votemper
da = da.where( (da.y > 250) & (da.y < 500) & (da.x > 100) & (da.x < 250), drop=True)

#print(da.lat[125,75].to_numpy())
#print(da.lon[125,75].to_numpy())

da = da.metpy.assign_crs({
    "grid_mapping_name": "lambert_conformal_conic",
    "standard_parallel": 60.0,
    "longitude_of_central_meridian": 300.0,
    "latitude_of_projection_origin": 55.0,
})

da = da.metpy.assign_y_x()

start = (59, -61)
end = (61, -59)
    
cross = cross_section(data, start, end).set_coords(('lon', 'lat'))
quit()

#start = (52.78262329, -52.21795273)
#end = (55.61572647, -48.81662369)

cross = cross_section(temperature, start, end).set_coords(('lat','lon'))
print(cross)




















quit()

#Produces heat content and temperature 
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

##################################################################################################################
#OPENING AND INITIAL PROCESSING OF THE NETCDF MODEL OUTPUT FILES

#text file of paths to non-empty model output
gridT_txt = run + '_filepaths/' + run + '_gridT_filepaths.txt'

#open the text files and get lists of the .nc output filepaths
with open(gridT_txt) as f: lines = f.readlines()
filepaths_gridT = [line.strip() for line in lines]

#open the files and look at e3t and votemper
preprocess_gridT = lambda ds: ds[['e3t','votemper']]
DS = xr.open_mfdataset(filepaths_gridT,preprocess=preprocess_gridT)

#add horizontal cell dims
DS[['e1t','e2t']] = e1t,e2t #add T cell dimensions as variables

#apply tmask (ie masking bathy)
DS = DS.where(tmask == 1)

#apply mask (if there is one)
if mask_choice == 'LSCR' or mask_choice == 'LS2k' or mask_choice == 'LS':
    DS.coords['mask'] = mask
    DS = DS.where(DS.mask == 1, drop=True)

##################################################################################################################
#CALCULATIONS

#constants needed for heat content calculations
refT = -1.8 #reference temperature [C]                              (Value from Paul's email)
rho_0 = 1026#1025 #density reference (const. value?( [kg/m^3]       (Value from Gillard paper)
C_p = 3992#3850 #specific heat capacity (const. value?) [J/kgK]     (Value from Gillard paper)

#loop through the 4 depths and save .nc files
for d in [50, 200, 1000, 2000]: #loop through depths
    DS_d = DS.where(DS.deptht < d, drop=True) #drop values below specified depth

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
