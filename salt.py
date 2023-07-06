#Produces heat content
#Rowan Brown
#17 May 2023

#outputs 16 netcdf files per run (and you get to choose one mask per run):
# - 4 x depths (50m, 200m, 1000m, 2000m)
# - 2 x parameters (heat content and average temperatures)
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
dir = run + '_salt/'
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
preprocess_gridT = lambda ds: ds[['e3t','vosaline']]
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

#constants needed for calculations
##refT = -1.8 #reference temperature [C]                              (Value from Paul's email)
##rho_0 = 1026#1025 #density reference (const. value?( [kg/m^3]       (Value from Gillard paper)
##C_p = 3992#3850 #specific heat capacity (const. value?) [J/kgK]     (Value from Gillard paper)
refS = 34.8 #reference salinity [PSU] (or 34.97 like in the gillard paper?)

#loop through the 4 depths and save .nc files
for d in [50, 200, 1000, 2000]: #loop through depths
    DS_d = DS.where(DS.deptht < d, drop=True) #drop values below specified depth

    #note: there are two main ideas below: "col" refers to the idea that we're looking at water-columnwise averages, ie so we can make maps later. On 
    #the other hand, "region" refers to regionwise averages, so that we can make time plots later.

    #masking shelves
    #NOTE: bathy is masked to avoid skewed understandings/results from the on-shelf values this section could be commented out if needed 
    bottom_slice = DS_d.vosaline.isel(deptht = -1).isel(time_counter = 0)
    bottom_slice_bool = bottom_slice.notnull()
    shelf_mask, temp = xr.broadcast(bottom_slice_bool, DS_d.vosaline.isel(time_counter=0))
    DS_d = DS_d.where(shelf_mask)

    #salinity averaged through time 
    #cell weights (col): divide cell volume by average cell volume in each column
    volumes = DS_d.e1t*DS_d.e3t*DS_d.e2t #volume of each cell
    avg_col_vol = volumes.mean(dim='deptht') #average cell volume in each column 
    weights = volumes/avg_col_vol #dataarray of weights 
    weights = weights.fillna(0)
    vosaline_col_weighted = DS_d.vosaline.weighted(weights) #salinity weighted relative to its column
    vosaline_avg_col = vosaline_col_weighted.mean(dim='deptht') #NOTE: skipna should be True if not blocking shelves
    vosaline_avg_col_time = vosaline_avg_col.mean(dim='time_counter') #finally getting (weighted) average salinity in each column throughout the whole run
    vosaline_avg_col_time.to_netcdf(run + '_salt/' + run + '_vosaline_timeAvg_' + mask_choice + str(d) + '.nc') #.nc with time-avg salinity in each column (ie for making maps)

    #salinity averaged in space
    #cell weights (region): divide cell volume by average cell volume in the whole masked region
    avg_cell_vol = volumes.mean(dim=['deptht','y_grid_T','x_grid_T'])
    weights = volumes/avg_cell_vol
    weights = weights.fillna(0)
    vosaline_region_weighted = DS_d.vosaline.weighted(weights) 
    vosaline_avg_region = vosaline_region_weighted.mean(dim=['deptht','y_grid_T','x_grid_T'],skipna=True)
    vosaline_avg_region.to_netcdf(run + '_salt/' + run + '_vosaline_spaceAvg_' + mask_choice + str(d) + '.nc')

    #heat content
    FWC = ((refS - DS_d.vosaline)/refS) * volumes 
    FWC_sum_deptht = FWC.sum(dim='deptht')
    FWC_avg_time = FWC_sum_deptht.mean(dim='time_counter')
    FWC_avg_time.to_netcdf(run + '_salt/' + run + '_FWC_timeAvg_' + mask_choice + str(d) + '.nc')
    FWC_sum_space = FWC_sum_deptht.sum(dim=['y_grid_T','x_grid_T'])
    FWC_sum_space.to_netcdf(run + '_salt/' + run + '_FWC_spaceSum_' + mask_choice + str(d) + '.nc')

quit()
DS['FWC'+str(d)] = ((refS - avgS)/refS) * DS_d.volT_total * 10**(-9)












preprocess_gridT = lambda ds: ds[['e3t','vosaline']] #desired variables: cell thickness and salinity
DS = xr.open_mfdataset(filepaths,preprocess=preprocess_gridT) #open dataset(s)
DS[['e1t','e2t']] = e1t,e2t #add T cell dims as variables
DS.coords['LS_convec_mask'] = (('y_grid_T', 'x_grid_T'), LS_convec_mask) #add mask as coords
DS = DS.where(DS.LS_convec_mask == 1, drop=True) #drop data outside of mask
refS = 34.8 #reference salinity [PSU] (or 34.97 like in the gillard paper?)

for d in [50, 200, 1000, 2000]: #loop through depths

    #volumes
    DS_d = DS.where(DS.deptht < d, drop=True) #drops values below specified depth
    DS_d['volT'] = DS_d.e1t*DS_d.e3t*DS_d.e2t #volumes of T cells
    DS_d['volT_total'] = DS_d.volT.sum(dim=['x_grid_T','y_grid_T','deptht']) #volume of region

    #salinities
    DS_d['vosaline_weighted'] = DS_d.volT*DS_d.vosaline #weighted salinities
    avgS = DS_d.vosaline_weighted.sum(dim=['x_grid_T','y_grid_T','deptht'])/DS_d.volT_total #average salinities
    DS['avgS'+str(d)] = avgS

    #FWC
    DS['FWC'+str(d)] = ((refS - avgS)/refS) * DS_d.volT_total * 10**(-9)



quit()

import numpy as np 
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import datetime
import matplotlib.dates as mdates
import os

pauls_nemo_dir = '/home/rowan/projects/rrg-pmyers-ad/pmyers/ANHA4/ANHA4-EPM152-S/'
filepaths = sorted([pauls_nemo_dir + file for file in os.listdir(pauls_nemo_dir) if file.endswith('gridT.nc')])#[0::600]

with xr.open_dataset('ANHA4_mesh_mask.nc') as DS:
    e1t = DS.e1t[0,:,:].rename({'y': 'y_grid_T','x': 'x_grid_T'}) #renames dims
    e2t = DS.e2t[0,:,:].rename({'y': 'y_grid_T','x': 'x_grid_T'})
    lons = np.array(DS.variables['nav_lon'])
    lats = np.array(DS.variables['nav_lat'])

with xr.open_dataset('ARGOProfiles_mask.nc') as DS:
    LS_convec_mask = DS.tmask.fillna(0).to_numpy()

preprocess_gridT = lambda ds: ds[['e3t','vosaline']]
with xr.open_mfdataset(filepaths,preprocess=preprocess_gridT) as DS:
    DS = DS

DS[['e1t','e2t']] = e1t,e2t #add T cell dimensions as variables
DS.coords['LS_convec_mask'] = (('y_grid_T', 'x_grid_T'), LS_convec_mask) #add mask as coords
DS = DS.where(DS.LS_convec_mask == 1, drop=True) #drop data outside of mask

refT = -1.8 #reference temperature [C]                              (Value from Paul's email)
rho_0 = 1026#1025 #density reference (const. value?( [kg/m^3]       (Value from Gillard paper)
C_p = 3992#3850 #specific heat capacity (const. value?) [J/kgK]     (Value from Gillard paper)

for d in [50, 200, 1000, 2000]: #loop through depths

    #volumes
    DS_d = DS.where(DS.deptht < d, drop=True) #drop values below specified depth
    DS_d['volT'] = DS_d.e1t*DS_d.e3t*DS_d.e2t #volumes of T cells
    DS_d['volT_total'] = DS_d.volT.sum(dim=['x_grid_T','y_grid_T','deptht']) #volume of region

    #temperatures
    DS_d['votemper_weighted'] = DS_d.volT*DS_d.votemper #weighted temps
    avgT = DS_d.votemper_weighted.sum(dim=['x_grid_T','y_grid_T','deptht'])/DS_d.volT_total #average temperature
    DS['avgT'+str(d)] = avgT

    #heat content (following integral)
    HC_integrand = (DS.votemper+refT)*DS_d.volT
    HC_integral = HC_integrand.sum(dim=['x_grid_T','y_grid_T','deptht'])#/DS_d.volT_total #average adjusted temperature
    DS['HC'+str(d)] = rho_0 * C_p * 10**(-12) * HC_integral





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

