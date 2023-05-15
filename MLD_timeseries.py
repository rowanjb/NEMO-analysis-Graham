#for creating timeseries plots of MLD thickness
#rowan brown
#May 5, 2023

import numpy as np 
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import datetime
import matplotlib.dates as mdates
import os

#specify the run
run = 'EPM155'

#directory of nemo output files on graham
nemo_output_dir = '/home/rowan/projects/rrg-pmyers-ad/pmyers/ANHA4/ANHA4-' + run + '-S/'

#list of filepaths for the gridT files
filepaths = sorted([nemo_output_dir + file for file in os.listdir(nemo_output_dir) if file.endswith('gridT.nc')])#[0::100]

#mesh file
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

