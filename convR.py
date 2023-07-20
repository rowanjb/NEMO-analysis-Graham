#Produces convective resistance
#Rowan Brown
#10 Jul 2023

#outputs netcdf files
# - 4 x depths (50m, 200m, 1000m, 2000m)
# - 3 x masks
# - 2 x output data "formats":
#   - convR in each column averaged across time, for mapping purposes (should this be updated so that the window can be spec'ed?) 
#   - total convR in the masked region, for plotting in time

import xarray as xr
import os
import numpy as np
import density

#user specs
run = 'EPM158' #specify the run
mask_choice = 'LSCR' #choose which mask; options are 'LSCR', 'LS2k', or 'LS'

#creating directory if doesn't already exist
dir = run + '_convR/'
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
preprocess_gridT = lambda ds: ds[['e3t','votemper','vosaline','somxl010']] #get desired variables only
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
#Note: calculations are based on the Introducing Lab 60 paper from Clark

g = 9.80665 #gravity

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

    #pre-calculations
    areas = DS_d.e1t*DS_d.e2t
    areas = areas.isel(deptht=0) #only need one slice
    area = areas.sum(dim=['x_grid_T','y_grid_T'])
    Th = DS_d.votemper.isel(deptht=-1) #temperature values in the deepest level
    Sh = DS_d.vosaline.isel(deptht=-1) #salinity values in the deepest level
    refDens = density.density(Sh,Th) #potential densities at (around) h
    dens = density.density(DS_d.vosaline,DS_d.votemper) #densities in each cell from surface to h

    #following the equation from "Introducing LAB60..."
    term1 = refDens*(DS_d.e3t.sum(dim='deptht')) #used e3t.sum instead of depth[-1] because term2 is integrated using e3t too
    term2 = dens*DS_d.e3t
    term2 = term2.sum(dim='deptht')
    integrand = term1 - term2
    convR_col = integrand*g #this is the representative value in each column, units are J/m3 or kg/m s2 (didn't both multiplying and dividing by area)
    convR_timePlot = convR_col*areas*DS_d.deptht.isel(deptht=-1) #multiply the J/m3 value by column area and depth to get the total J  #/area #multiplying by cell area and dividing by total area (i.e., essentially weighting the values)
    convR_timePlot = convR_timePlot.sum(dim=['x_grid_T','y_grid_T']) #summing to get the total J in in the masked area #summing the weighted values spatially, which gives the mean convR in the mask
    convR_col = convR_col.mean(dim='time_counter') #taking the mean in time, which gives the mean convR in each column throughout the run
    
    #dropping deptht dim
    convR_timePlot = convR_timePlot.drop_vars('deptht')
    convR_col = convR_col.drop_vars('deptht')

    #saving
    #convR_col.to_netcdf(run + '_convR/' + run + '_convR_map_' + mask_choice + str(d) + '.nc')
    convR_timePlot.to_netcdf(run + '_convR/' + run + '_sumConvR_plot_' + mask_choice + str(d) + '.nc') 





quit()

convE = np.multiply(np.multiply(integrand,areas),np.divide(g,areas))
convE = convE.where(refDens>1000)

##drop data outside mask
#convE.coords['LS_convec_mask'] = (('y_grid_T', 'x_grid_T'), LS_convec_mask) #add mask as coords
#convE = convE.where(convE.LS_convec_mask == 1, drop=True) #drop data outside of mask

#calculating area mean
convEmean = convE.mean(dim=["y_grid_T", "x_grid_T"])
convEmean2 = convEmean.mean(dim="time_counter")
#minmax = 0, 4000 #alternatively, can assign min and max values manually
#
##plotting and saving maps/figures
#CBlabel = 'Convective energy ($J$ $m^{-3}$)'
#title = 'Convective energy (EPM152)'
#fileName  = 'ConvE_pics_EPM152/LS_convective_energy_EPM152_'
#for i,time in enumerate(convE.time_counter):
#    LSmap.LSmap(convE.isel(time_counter=i),lons,lats,minmax,CBlabel,title,fileName)



quit()



#Produces FWC and average salinity  
#Rowan Brown
#17 May 2023

#outputs netcdf files
# - 4 x depths (50m, 200m, 1000m, 2000m)
# - 2 x parameters (FWC and average salinity)
# - 3 x masks
# - 2 x output data "formats":
#   - FWC/salinity in each column averaged across time, for mapping purposes (should this be updated so that the window can be spec'ed?)
#   - total FWC/averaged salinity in the masked region, for plotting in time

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

#open the files and look at e3t and vosaline
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


