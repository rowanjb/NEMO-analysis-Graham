#Produces heat content 
#Rowan Brown
#17 May 2023

import numpy as np 
import pandas as pd
import xarray as xr
import os

#user specs
run = 'EPM151' #specify the run
mask_choice = 'LSCR' #choose which mask; options are 'LSCR', 'LS2k', or 'LS'

#creating directory if doesn't already exist
dir = run + '_heat/'
if not os.path.exists(dir):
    os.makedirs(dir)


##################################################################################################################
#MASKS

#mask for land, bathymetry, etc. and horiz. grid dimensions
with xr.open_dataset('masks/ANHA4_mesh_mask.nc') as DS:
    tmask = DS.tmask[0,:,:,:].to_numpy() #DataArray with dims (t: 1, z: 50, y: 800, x: 544) 
    e1t = DS.e1t[0,:,:].rename({'y': 'y_grid_T','x': 'x_grid_T'}) #renames dims
    e2t = DS.e2t[0,:,:].rename({'y': 'y_grid_T','x': 'x_grid_T'})

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

#apply mask (if there is one)
if mask_choice == 'LSCR' or mask_choice == 'LS2k' or mask_choice == 'LS':
    DS.coords['mask'] = mask
    DS = DS.where(DS.mask == 1, drop=True)

##################################################################################################################
#CALCULATIONS

refT = -1.8 #reference temperature [C]                              (Value from Paul's email)
rho_0 = 1026#1025 #density reference (const. value?( [kg/m^3]       (Value from Gillard paper)
C_p = 3992#3850 #specific heat capacity (const. value?) [J/kgK]     (Value from Gillard paper)

#want to output:
# - avg temp in the columns for all 4 depths across time for mapping (all time???? or equal time windows) in all 3 masks    =12 files?
# - total heat in the columns for all 4 depths across time for mapping (all time???? or equal time windows) in all 3 masks    =12 files?
# - average temp in the 3 masks for all 4 depths across time    =12 files?
# - total heat content in the 3 masks for all 4 depths acrss time   =12 files?

#loop through the 4 depths and save .nc files
for d in [50, 200, 1000, 2000]: #loop through depths

    DS_d = DS.where(DS.deptht < d, drop=True) #drop values below specified depth

    #temperature
    DS_d['votemper_avg_deptht'] = DS_d.votemper.mean(dim='deptht') 
    DS_d['votemper_avg_time'] = DS_d.votemper_avg_deptht.mean(dim='time_counter') 
    DS_d.votemper_avg_time.to_netcdf(run + '_heat/' + run + '_votemper_timeAvg_' + mask_choice + str(d) + '.nc') #.nc with time-avg temp in each column (ie for making maps)
    DS_d['votemper_avg_space'] = DS_d.votemper_avg_deptht.mean(dim=['y_grid_T','x_grid_T']) 
    DS_d.votemper_avg_space.to_netcdf(run + '_heat/' + run + '_votemper_spaceAvg_' + mask_choice + str(d) + '.nc') #.nc with region-avg temp through time (ie for making time plots)
    #DS_d.votemper_avg_deptht.to_netcdf('heat/votemper_' + run + '_' + str(d) + '.nc')

    #heat content
    DS_d['volT'] = DS_d.e1t*DS_d.e3t*DS_d.e2t #volumes of T cells (IS THIS A LEGITIMATE WAY OF MULTIPLYING??????)
    DS_d['HC'] = rho_0 * C_p * 10**(-12) * (DS.votemper - refT) * DS_d.volT  #should be T-Tref, i.e.,  minus??????????????????????????
    DS_d['HC_sum_deptht'] = DS_d.HC.sum(dim='deptht')
    DS_d['HC_avg_time'] = DS_d.HC_sum_deptht.mean(dim='time_counter')
    DS_d.HC_avg_time.to_netcdf(run + '_heat/' + run + '_HC_timeAvg_' + mask_choice + str(d) + '.nc') #.nc with time-avg total HC in each column (ie for making maps)
    DS_d['HC_sum_space'] = DS_d.HC_sum_deptht.sum(dim=['y_grid_T','x_grid_T'])
    DS_d.HC_sum_space.to_netcdf(run + '_heat/' + run + '_HC_spaceSum_' + mask_choice + str(d) + '.nc') #.nc with region-sum HC through time (ie for making time plots)
    #DS_d.HC_sum.to_netcdf('heat/HC_' + run + '_' + str(d) + '.nc')

quit()

dates = DS.indexes['time_counter'].to_datetimeindex(unsafe=True) #Beware: warning turned off!!
dates = [d.date() for d in dates]
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=800)) 
plt.plot(dates, DS.HC50, label = "Top ~50m") 
plt.plot(dates, DS.HC200, label = "Top ~200m")
plt.plot(dates, DS.HC1000, label = "Top ~1000m")
plt.plot(dates, DS.HC2000, label = "Top ~2000m")
plt.legend()
plt.xticks(rotation=45)
plt.title('Heat content in the LS convection region, EPM155')
plt.ylabel('Heat content (TJ)')
plt.xlabel('Time')
plt.savefig('temp-EPM155_HC_convectiveRegion.png', dpi=1200, bbox_inches="tight")
plt.close()

dates = DS.indexes['time_counter'].to_datetimeindex(unsafe=True) #Beware: warning turned off!!
dates = [d.date() for d in dates]
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=800))
plt.plot(dates, DS.avgT50, label = "Top ~50m")
plt.plot(dates, DS.avgT200, label = "Top ~200m")
plt.plot(dates, DS.avgT1000, label = "Top ~1000m")
plt.plot(dates, DS.avgT2000, label = "Top ~2000m")
plt.legend()
plt.xticks(rotation=45)
plt.title('Average surface temperature in the LS convection region, EPM155')
plt.ylabel('Temperature (degrees Celsius)')
plt.xlabel('Time')
plt.savefig('temp-EPM155_Temperature_convectiveRegion.png', dpi=1200, bbox_inches="tight")
plt.close()
