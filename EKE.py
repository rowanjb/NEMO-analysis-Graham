#exports dataarray of EKE for ANHA4 runs
#Rowan Brown
#May 5, 2023

import numpy as np 
import xarray as xr
import os

#user specs
run = 'EPM151' #specify the run
window = 5 #specify the rolling window
maxDepth = 450 #specify the integration depths 

#mask for land, bathymetry, etc. to reduce computational cost
with xr.open_dataset('ANHA4_mesh_mask.nc') as DS:
    tmask = DS.tmask[0,:,:,:].to_numpy() #DataArray with dims (t: 1, z: 50, y: 800, x: 544) 

#getting the grid T (I think, check this) lats and lons
with xr.open_dataset('ANHA4_mesh_mask.nc') as DS:
    lons = DS.variables['nav_lon']
    lats = DS.variables['nav_lat']

#text files with lists of all non-empty model outputs
gridU_txt = run + '_filepaths/' + run + '_gridU_filepaths.txt'
gridV_txt = run + '_filepaths/' + run + '_gridV_filepaths.txt'

#open the text files and get lists of the .nc output filepaths
with open(gridU_txt) as f: lines = f.readlines()
filepaths_gridU = [line.strip() for line in lines]
with open(gridV_txt) as f: lines = f.readlines()
filepaths_gridV = [line.strip() for line in lines]

#preprocessing
preprocess_gridU = lambda ds: ds[['e3u','vozocrtx']] #desired variables
preprocess_gridV = lambda ds: ds[['e3v','vomecrty']] #desired variables

#open the datasets
DSU = xr.open_mfdataset(filepaths_gridU,preprocess=preprocess_gridU,engine="netcdf4") #opens dataset
DSV = xr.open_mfdataset(filepaths_gridV,preprocess=preprocess_gridV,engine="netcdf4") #opens dataset

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

#re-mapping x and y so they're consistent with the T grid
DSU = DSU.assign_coords(x=DSU.x-0.5)
DSV = DSV.assign_coords(y=DSV.y+0.5)

#EKE calculations (change back to 5 for actual calculations)
DSU_bar_sqr = (DSU-DSU.rolling(time_counter=window,center=True).mean())**2 
DSV_bar_sqr = (DSV-DSV.rolling(time_counter=window,center=True).mean())**2
EKE = (DSU_bar_sqr.vozocrtx + DSV_bar_sqr.vomecrty)/2 #DataArray

#dropping unnecessary coordinate
EKE = EKE.drop_vars('time_centered')

#add grid T lat and lons ####and drop values outside the Labrador Sea 
EKE.coords['nav_lat'] = (('y', 'x'), lats) 
EKE.coords['nav_lon'] = (('y', 'x'), lons)
#EKE = EKE.where(EKE.nav_lat > 50, drop=True)
#EKE = EKE.where(EKE.nav_lat < 70, drop = True)
#EKE = EKE.where(EKE.nav_lon > -65, drop=True)
#EKE = EKE.where(EKE.nav_lon < -40, drop=True)

##masking the LS convection region
#with xr.open_dataset('ARGOProfiles_mask.nc') as DS:
#    LS_convec_mask = DS.tmask.fillna(0).to_numpy()
#EKE.coords['LS_convec_mask'] = (('y', 'x'), LS_convec_mask) #add mask as coords
#EKE = EKE.where(EKE.LS_convec_mask == 1)#, drop=True) #drop data outside of mask
#EKE = EKE.drop_vars('LS_convec_mask')

#dropping below a specified depth 
EKE = EKE.where(EKE.z < maxDepth, drop=True) #drop data outside of mask

#getting time-averaged pelagic EKE 
notnulls = EKE.isel(time_counter=3).isel(z=-1).notnull() #identifying shelves
EKE = EKE.sum(dim='z') #summing in z direction
EKE = EKE.mean(dim='time_counter') #taking average in time
EKE = EKE.where(notnulls) #turning values on the shelves to NaNs

#dropping (more) unnecessary coordinates
EKE = EKE.drop_vars(['time_counter','z'])

#Saving
EKE.to_netcdf('EKE_avg_' + run + '_' + str(maxDepth) + '.nc')
