###you're gonna have to make an nc file for each day :(


#exports dataarray of EKE in each cell for ANHA4 runs
#Rowan Brown
#May 5, 2023

import numpy as np 
import xarray as xr
import os

#specify the run
run = 'EPM151'

#mask for land, bathymetry, etc. to reduce computational cost
with xr.open_dataset('ANHA4_mesh_mask.nc') as DS:
    tmask = DS.tmask[0,:,:,:].to_numpy() #DataArray with dims (t: 1, z: 50, y: 800, x: 544) 

#I have text files that list all the non-empty model runs 
#there is one text file per .nc type, i.e. gridT, gridW, icemod, etc.
#each run has a folder (e.g. EPM151_filepaths) containing the associated text files
#the gridV and gridU paths are:
gridU_txt = run + '_filepaths/' + run + '_gridU_filepaths.txt'
gridV_txt = run + '_filepaths/' + run + '_gridV_filepaths.txt'

#open the text files and get lists of the .nc output filepaths
with open(gridU_txt) as f: 
    lines = f.readlines()
filepaths_gridU = [line.strip() for line in lines]
with open(gridV_txt) as f: 
    lines = f.readlines()
filepaths_gridV = [line.strip() for line in lines]

#open the datasets
preprocess_gridU = lambda ds: ds[['e3u','vozocrtx']] #desired variables
DSU = xr.open_mfdataset(filepaths_gridU[::600],preprocess=preprocess_gridU) #opens dataset
preprocess_gridV = lambda ds: ds[['e3v','vomecrty']] #desired variables
DSV = xr.open_mfdataset(filepaths_gridV[::600],preprocess=preprocess_gridV) #opens dataset

#renaming dimensions so that they are the same for both velocity components
DSU = DSU.rename({'depthu': 'z'})  
DSV = DSV.rename({'depthv': 'z'}) 

#apply tmask
DSV.coords['tmask'] = (('z', 'y', 'x'), tmask) #add mask as coords
DSV = DSV.where(DSV.tmask == 1) #drop data outside of mask
DSU.coords['tmask'] = (('z', 'y', 'x'), tmask) #add mask as coords
DSU = DSU.where(DSU.tmask == 1) #drop data outside of mask

#co-locate the velocities onto the T grid 
DSU = DSU.interp(x=DSU.x+0.5)
DSV = DSV.interp(y=DSV.y-0.5)

#EKE calculations
DSU_bar_sqr = (DSU-DSU.rolling(time_counter=5,center=True).mean())**2 
DSV_bar_sqr = (DSV-DSV.rolling(time_counter=5,center=True).mean())**2
EKE = (DSU_bar_sqr.vozocrtx + DSV_bar_sqr.vomecrty)/2 #DataArray

EKE.drop_vars('time_centered')

print(EKE)
quit()

EKE.to_netcdf('EKE_' + run + '.nc')
