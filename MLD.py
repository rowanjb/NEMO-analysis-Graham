#Produces MLD (average and maximum)
#Rowan Brown
#17 May 2023

#outputs netcdf files
# - 2 x parameters (heat content and average temperatures)
# - 3 x masks
# - 2 x output data "formats":
#   - Average/max MLD in each column across time, for mapping purposes (should this be updated so that the window can be spec'ed?)
#   - Average/max MLD in the masked region, for plotting in time

import numpy as np
import pandas as pd
import xarray as xr
import os

#user specs
run = 'EPM158' #specify the run
mask_choice = 'LS2k' #choose which mask; options are 'LSCR', 'LS2k', or 'LS'

#creating directory if doesn't already exist
dir = run + '_MLD/'
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

#open the files and look at e3t and sohmld
preprocess_gridT = lambda ds: ds[['e3t','somxl010']]
DS = xr.open_mfdataset(filepaths_gridT,preprocess=preprocess_gridT)

#add horizontal cell dims
DS[['e1t','e2t']] = e1t,e2t #add T cell dimensions as variables

#apply tmask (ie masking bathy)
DS = DS.where(tmask == 1)

#apply mask (if there is one)
if mask_choice == 'LSCR' or mask_choice == 'LS2k' or mask_choice == 'LS':
    DS.coords['mask'] = mask
    DS = DS.where(DS.mask == 1, drop=True)

#selecting only one depth slice since MLD is saved in the water column as (for e.g.) [10.2,10.2,10.2,10.2,etc.]
MLD = DS.somxl010.isel(deptht = 0)

##################################################################################################################
#CALCULATIONS

#note: there are two main ideas below: "col" refers to the idea that we're looking at water-columnwise values, ie so we can make maps later. On 
#the other hand, "region" refers to regionwise values, so that we can make time plots later.

##masking shelves
##NOTE: bathy is masked to avoid skewed understandings/results from the on-shelf values this section could be commented out if needed 
#bottom_slice = DS_d.vosaline.isel(deptht = -1).isel(time_counter = 0)
#bottom_slice_bool = bottom_slice.notnull()
#shelf_mask, temp = xr.broadcast(bottom_slice_bool, DS_d.vosaline.isel(time_counter=0))
#DS_d = DS_d.where(shelf_mask)

#max MLD
maxMLD_col = MLD.max(dim=['time_counter'], skipna=True) #max MLD in each column during the whole period (i.e., for mapping reasons)
maxMLD_region = MLD.max(dim=['y_grid_T','x_grid_T'], skipna=True) #max MLD in the masked region for each time-step (i.e., for time-plotting reasons)

#average MLD
areas = DS.e1t*DS.e2t
areas = areas.isel(deptht = 0)
avgArea = areas.mean(dim=['y_grid_T','x_grid_T'])
weights = areas/avgArea #CHECK THAT THIS IS RIGHT!!!!!!!!!!!!!!!!!!!!!!!!!!
weights = weights.fillna(0)
MLD = MLD.weighted(weights)
avgMLD_col = MLD.mean(dim='time_counter',skipna=True) #average MLD in each column during the whole period
avgMLD_region = MLD.mean(dim=['y_grid_T','x_grid_T'],skipna=True) 

#saving
maxMLD_col.to_netcdf(run + '_MLD/' + run + '_max_MLD_map_' + mask_choice + '.nc')
maxMLD_region.to_netcdf(run + '_MLD/' + run + '_max_MLD_time_plot_' + mask_choice + '.nc')
avgMLD_col.to_netcdf(run + '_MLD/' + run + '_avg_MLD_map_' + mask_choice + '.nc')
avgMLD_region.to_netcdf(run + '_MLD/' + run + '_avg_MLD_time_plot_' + mask_choice + '.nc')












#Calculations
quit()
avgMLD = DS.mean(dim=['y_grid_T', 'x_grid_T'], skipna=True)*(-1)
maxMLD = DS.max(dim=['y_grid_T', 'x_grid_T'], skipna=True)*(-1)


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

                                                                                                                                     















with xr.open_dataset('ANHA4_mesh_mask.nc') as DS:
    e1t = DS.e1t[0,:,:].rename({'y': 'y_grid_T','x': 'x_grid_T'}) #renames dims
    e2t = DS.e2t[0,:,:].rename({'y': 'y_grid_T','x': 'x_grid_T'})
    lons = np.array(DS.variables['nav_lon']) #I'm pretty sure these are gridT lat and lon values
    lats = np.array(DS.variables['nav_lat'])

#mask file (try get a faster way that doesn't require to_numpy()
with xr.open_dataset('ARGOProfiles_mask.nc') as DS:
    LS_convec_mask = DS.tmask.fillna(0).to_numpy()

#open the datasets 
preprocess_gridT = lambda ds: ds[['e3t','sohmld']]
DS = xr.open_mfdataset(filepaths,data_vars='minimal',coords='minimal',preprocess=preprocess_gridT)
DS[['e1t','e2t']] = e1t,e2t #add T cell dimensions as variables
DS.coords['LS_convec_mask'] = (('y_grid_T', 'x_grid_T'), LS_convec_mask) #add mask as coords
DS = DS.where(DS.LS_convec_mask == 1, drop=True) #drop data outside of mask

#Calculations
avgMLD = DS.mean(dim=['y_grid_T', 'x_grid_T'], skipna=True)*(-1)
maxMLD = DS.max(dim=['y_grid_T', 'x_grid_T'], skipna=True)*(-1)

#plotting
dates = [d.date() for d in DS.indexes['time_counter'].to_datetimeindex(unsafe=True)] #Beware: warning turned off!!
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))#'%m/%d/%Y'
plt.gca().xaxis.set_major_locator(mdates.YearLocator(base=2)) 
plt.plot(dates, avgMLD.sohmld, label = "Mean MLD")
plt.plot(dates, maxMLD.sohmld, label = "Maximum MLD")
plt.legend(loc='center left', bbox_to_anchor=(1,0.5))
plt.gca().set_ylim(top=0)
plt.title('MLD in the LS convection region, EPM155')
plt.ylabel('Mixed layer depth ($m$)')
plt.xlabel('Time')
plt.savefig('temp-EPM155_MLD_convectiveRegion.png', dpi=1200, bbox_inches="tight")
plt.close()

