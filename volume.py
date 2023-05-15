#get volumes of grid T cells (could add functionality for grid U and V too)
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
run = 'EPM151'

#directory of nemo output files on graham
nemo_output_dir = '/home/rowan/projects/rrg-pmyers-ad/pmyers/ANHA4/ANHA4-' + run + '-S/'

#list of filepaths for the gridU and gridV files
filepaths = sorted([nemo_output_dir + file for file in os.listdir(nemo_output_dir) if file.endswith('gridT.nc')])#[0::100]

#getting horizontal cell dimensions
with xr.open_dataset('ANHA4_mesh_mask.nc') as DS:
    e1t = DS.e1t[0,:,:].rename({'y': 'y_grid_T','x': 'x_grid_T'}) #renames dims
    e2t = DS.e2t[0,:,:].rename({'y': 'y_grid_T','x': 'x_grid_T'}) #note first dim is t:1
#    lons = np.array(DS.variables['nav_lon'])
#    lats = np.array(DS.variables['nav_lat'])

#with xr.open_dataset('ARGOProfiles_mask.nc') as DS:
#    LS_convec_mask = DS.tmask.fillna(0).to_numpy()

#getting vertical cell dimensions
preprocess_gridT = lambda ds: ds[['e3t']]
DS = xr.open_mfdataset(filepaths,preprocess=preprocess_gridT)#[:-2],data_vars='minimal',coords='minimal',preprocess=preprocess_gridT)

#joining cell dimensions
DS[['e1t','e2t']] = e1t,e2t #add T cell dimensions as variables
#DS.coords['LS_convec_mask'] = (('y_grid_T', 'x_grid_T'), LS_convec_mask) #add mask as coords
#DS = DS.where(DS.LS_convec_mask == 1, drop=True) #drop data outside of mask

#volumes dataarray
volumes = DS.e1t*DS.e3t*DS.e2t 

#save the volumes dataarray
volumes.to_netcdf('volumes_' + run + '.nc')
