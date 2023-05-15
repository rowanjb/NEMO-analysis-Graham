#outputs timeseries plots (of EKE, currently) 
#Rowan Brown
#May 5, 2023

import numpy as np 
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import datetime
import matplotlib.dates as mdates
import os

#run
run = 'EPM151-short'

#file to open
ncfile = 'EKE_' + run + '.nc'

#open nc file
da = xr.open_dataarray(ncfile)

#cell volumes


#directory of nemo output files on graham
nemo_output_dir = '/home/rowan/projects/rrg-pmyers-ad/pmyers/ANHA4/ANHA4-' + run + '-S/'

#list of filepaths for the gridU and gridV files
filepaths_gridU = sorted([nemo_output_dir + file for file in os.listdir(nemo_output_dir) if file.endswith('gridU.nc')])#[0::600]
filepaths_gridV = sorted([nemo_output_dir + file for file in os.listdir(nemo_output_dir) if file.endswith('gridV.nc')])#[0::600]

#ANHA4 mesh file
with xr.open_dataset('ANHA4_mesh_mask.nc') as DS:
    e1u = DS.e1u[0,:,:].rename({'y': 'y_grid_T','x': 'x_grid_T'})
    e2u = DS.e2u[0,:,:].rename({'y': 'y_grid_T','x': 'x_grid_T'})
    e1v = DS.e1v[0,:,:].rename({'y': 'y_grid_T','x': 'x_grid_T'})
    e2v = DS.e2v[0,:,:].rename({'y': 'y_grid_T','x': 'x_grid_T'})
    lons = np.array(DS.variables['nav_lon'])
    lats = np.array(DS.variables['nav_lat'])

##convection region mask
##does this work for all t and v and u grids?
#with xr.open_dataset('RGOProfiles_mask.nc') as DS:
#    LS_convec_mask = DS.tmask.fillna(0).to_numpy()

#open the datasets
preprocess_gridU = lambda ds: ds[['e3u','vozocrtx']] #desired variables
DSU = xr.open_mfdataset(filepaths_gridU,preprocess=preprocess_gridU) #opens dataset
preprocess_gridV = lambda ds: ds[['e3v','vomecrty']] #desired variables
DSV = xr.open_mfdataset(filepaths_gridV,preprocess=preprocess_gridV) #opens dataset

#co-locate the velocities 
DSU = DSU.interp(x=DSU.x+0.5)
DSV = DSV.interp(y=DSV.y-0.5)

#unnecessary 
###DSU = DSU.drop(labels='x')
###DSV = DSV.drop(labels='y')
###
###DSU.coords['LS_convec_mask'] = (('y', 'x'), LS_convec_mask) #add mask as coords
###DSV.coords['LS_convec_mask'] = (('y', 'x'), LS_convec_mask) #add mask as coords
###
###DSU = DSU.where(DSU.LS_convec_mask == 1, drop=True) #drop data outside of mask
###DSV = DSV.where(DSV.LS_convec_mask == 1, drop=True) #drop data outside of mask

##renaming dimensions so that they are the same for both velocity components
DSU = DSU.rename({'depthu': 'depth'})  
DSV = DSV.rename({'depthv': 'depth'}) 

#EKE calculations
DSU_bar_sqr = (DSU-DSU.rolling(time_counter=5,center=True).mean())**2 
DSV_bar_sqr = (DSV-DSV.rolling(time_counter=5,center=True).mean())**2
EKE = (DSU_bar_sqr.vozocrtx + DSV_bar_sqr.vomecrty)/2 #DataArray

EKE.to_netcdf("test.nc")


quit()

dates = EKE.indexes['time_counter'].to_datetimeindex(unsafe=True) #Beware: warning turned off!!
dates = [d.date() for d in dates]

#plt.rc('text', usetex=True)
#plt.rc('font', family='serif')

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))#'%m/%d/%Y'
plt.gca().xaxis.set_major_locator(mdates.YearLocator(base=2))

#plt.plot(dates151, DS151.HC50, label = "EPM151, top ~50m", color='blue') 
#plt.plot(dates151, DS151.HC200, label = "EPM151, top ~200m", color='orange')
#plt.plot(dates151, DS151.HC1000, label = "EPM151, top ~1000m", color='green')
plt.plot(dates, EKE.sum(dim=['depth', 'y', 'x']))#, label = "EPM151, top ~2000m")#, color='red')

#plt.legend(loc='center left', bbox_to_anchor=(1,0.5))
#plt.xticks(rotation=45)
plt.title('EKE in the LS convection region')
plt.ylabel('EKE ($J$)')
plt.xlabel('Time')
plt.savefig('temp-EPM151_EKE_convectiveRegion.png', dpi=1200, bbox_inches="tight")
plt.close()

quit()
