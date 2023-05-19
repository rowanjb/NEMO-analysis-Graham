#Produces heat content 
#Rowan Brown
#17 May 2023

import numpy as np 
import pandas as pd
import xarray as xr
import os

#specify the run
run = 'EPM151'

#mask for land, bathymetry, etc. and horiz. grid dimensions
with xr.open_dataset('ANHA4_mesh_mask.nc') as DS:
    tmask = DS.tmask[0,:,:,:].to_numpy() #DataArray with dims (t: 1, z: 50, y: 800, x: 544) 
    e1t = DS.e1t[0,:,:].rename({'y': 'y_grid_T','x': 'x_grid_T'}) #renames dims
    e2t = DS.e2t[0,:,:].rename({'y': 'y_grid_T','x': 'x_grid_T'})

#text file of paths to non-empty model output
gridT_txt = run + '_filepaths/' + run + '_gridT_filepaths.txt'

#open the text files and get lists of the .nc output filepaths
with open(gridT_txt) as f: lines = f.readlines()
filepaths_gridT = [line.strip() for line in lines][:3]

#with xr.open_dataset('ARGOProfiles_mask.nc') as DS:
#    LS_convec_mask = DS.tmask.fillna(0).to_numpy()

preprocess_gridT = lambda ds: ds[['e3t','votemper']]
DS = xr.open_mfdataset(filepaths_gridT,preprocess=preprocess_gridT)

#add horizontal cell dims
DS[['e1t','e2t']] = e1t,e2t #add T cell dimensions as variables

#LS convection region mask---MAYBE LEAVE THIS UNTIL A LATER SCRIPT? (IE PLOTTING)
#DS.coords['LS_convec_mask'] = (('y_grid_T', 'x_grid_T'), LS_convec_mask) #add mask as coords
#DS = DS.where(DS.LS_convec_mask == 1, drop=True) #drop data outside of mask

refT = -1.8 #reference temperature [C]                              (Value from Paul's email)
rho_0 = 1026#1025 #density reference (const. value?( [kg/m^3]       (Value from Gillard paper)
C_p = 3992#3850 #specific heat capacity (const. value?) [J/kgK]     (Value from Gillard paper)

#output .nc files with average temperature and total heat content per column down to given depths
for d in [50, 200, 1000, 2000]: #loop through depths

    #average temperature in the water columns
    DS_d = DS.where(DS.deptht < d, drop=True) #drop values below specified depth
    DS_d['votemper_avg'] = DS_d.votemper.mean(dim='deptht')
    DS_d.votemper_avg.to_netcdf('heat/votemper_' + run + '_' + str(d) + '.nc') 

    #heat content in the water columns
    DS_d['volT'] = DS_d.e1t*DS_d.e3t*DS_d.e2t #volumes of T cells
    DS_d['HC'] = rho_0 * C_p * 10**(-12) * (DS.votemper - refT) * DS_d.volT  #should be T-Tref, i.e.,  minus??????????????????????????
    DS_d['HC_sum'] = DS_d.HC.sum(dim='deptht')
    DS_d.HC_sum.to_netcdf('heat/HC_' + run + '_' + str(d) + '.nc')

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
