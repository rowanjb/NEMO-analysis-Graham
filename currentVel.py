#Produces current velocities down to 4 depths
#Co-located U and V velocities can be used with quiver to make maps
#Rowan Brown
#17 May 2023

#outputs netcdf files
# - 4 x depths (50m, 200m, 1000m, 2000m)
# - 3 x masks
# - velocities in each column averaged across time, for mapping purposes (should this be updated so that the window can be spec'ed?) 

import numpy as np 
import pandas as pd
import xarray as xr
import os

def currentVelocity(run,mask_choice):

    #creating directory if doesn't already exist
    dir = run + '_currentVel/'
    if not os.path.exists(dir):
        os.makedirs(dir)

    ##################################################################################################################
    #MASKS

    #mask for land, bathymetry, etc. and horiz. grid dimensions
    with xr.open_dataset('masks/ANHA4_mesh_mask.nc') as DS:
        tmask = DS.tmask[0,:,:,:].rename({'y': 'y_grid_T', 'x': 'x_grid_T'}) #DataArray with dims (t: 1, z: 50, y: 800, x: 544) 
        #e1t = DS.e1t[0,:,:].rename({'y': 'y_grid_T', 'x': 'x_grid_T'})
        #e2t = DS.e2t[0,:,:].rename({'y': 'y_grid_T', 'x': 'x_grid_T'})

    if mask_choice == 'LS2k': #mask for 2000m depth interior area
        mask = xr.open_dataarray('masks/mask_LS_2k.nc').astype(int)
    elif mask_choice == 'LS': #mask for entire LS region
        mask = xr.open_dataarray('masks/mask_LS.nc').astype(int)
    elif mask_choice == 'LSCR': #mask for LS convection region
        mask = xr.open_dataset('masks/ARGOProfiles_mask.nc').tmask.astype(int).rename({'x':'x_grid_T','y':'y_grid_T'})
    else: 
        print("Y'all didn't choose a mask")
        quit()

    #################################################################################################################
    #OPENING AND INITIAL PROCESSING OF THE NETCDF MODEL OUTPUT FILES

    #these are text files with lists of all non-empty model outputs (made with 'filepaths.py')
    gridU_txt = run + '_filepaths/' + run + '_gridU_filepaths.txt'
    gridV_txt = run + '_filepaths/' + run + '_gridV_filepaths.txt'
    gridT_txt = run + '_filepaths/' + run + '_gridT_filepaths.txt'

    #open the text files and get lists of the .nc output filepaths
    with open(gridU_txt) as f: lines = f.readlines()
    filepaths_gridU = [line.strip() for line in lines]
    with open(gridV_txt) as f: lines = f.readlines()
    filepaths_gridV = [line.strip() for line in lines]
    with open(gridT_txt) as f: lines = f.readlines()
    filepaths_gridT = [line.strip() for line in lines]

    #preprocessing (specifying variables that we need and ignoring the rest)
    preprocess_gridU = lambda ds: ds[['e3u','vozocrtx']]
    preprocess_gridV = lambda ds: ds[['e3v','vomecrty']]
    preprocess_gridT = lambda ds: ds[['e3t','vosaline']] #vosaline is for masking later

    #open the datasets
    DSU = xr.open_mfdataset(filepaths_gridU,preprocess=preprocess_gridU,engine="netcdf4")
    DSV = xr.open_mfdataset(filepaths_gridV,preprocess=preprocess_gridV,engine="netcdf4")
    DST = xr.open_mfdataset(filepaths_gridT,preprocess=preprocess_gridT,engine="netcdf4")

    ##add horizontal cell dimensions as variables 
    #DST = DST.assign(e1t=e1t,e2t=e2t)

    #renaming dimensions so that they are the same for all datasets
    DSU = DSU.rename({'depthu': 'z', 'y': 'y_grid_T', 'x': 'x_grid_T'})
    DSV = DSV.rename({'depthv': 'z', 'y': 'y_grid_T', 'x': 'x_grid_T'})
    DST = DST.rename({'deptht': 'z'})

    ##apply tmask (i.e., masking bathy)
    ##THIS PROBABLY ISN'T NECESSARY??????
    #DSU = DSU.where(tmask == 1)
    #DSV = DSV.where(tmask == 1)
    #DST = DST.where(tmask == 1)

    ##################################################################################################################
    #CALCULATIONS

    #first, velocities are co-located on the T grid:
    DSU = DSU.interp(x_grid_T = DSU.x_grid_T - 0.5) 
    DSV = DSV.interp(y_grid_T = DSV.y_grid_T - 0.5)

    #re-mapping 'x' and 'y' so they're consistent with the T grid
    DSU = DSU.assign_coords(x_grid_T = DSU.x_grid_T + 0.5)
    DSV = DSV.assign_coords(y_grid_T = DSV.y_grid_T + 0.5)

    #adding velocities to the T-grid
    DST = DST.assign(U=DSU.vozocrtx)#['U'] = DSU.vozocrtx
    DST = DST.assign(V=DSV.vomecrty)#var['V'] = DSV.vomecrty

    #print(DST.nav_lon_grid_T[400,200].to_numpy())
    #print(DST.nav_lon[400,200].to_numpy())
    #quit()

    #nav_lat and nav_lat_grid_T should be pretty damn close now (circa Aug 31 2023)
    #ie within around 5-10m
    DST = DST.drop_vars(['nav_lat','nav_lon','e3t'])

    #renaming depth dim/var if mask is LS or LS2k
    if mask_choice == 'LS' or mask_choice == 'LS2k':
        mask = mask.rename({'deptht':'z'})

    #apply mask (if there is one)
    if mask_choice == 'LSCR' or mask_choice == 'LS2k' or mask_choice == 'LS':
        DST = DST.where(mask == 1, drop=True)

    #loop through the 4 depths and save .nc files
    for d in [50, 200, 1000, 2000]: #loop through depths
        DS_d = DST.where(DST.z < d, drop=True) #drop values below specified depth

        ##masking shelves
        ##NOTE: bathy is masked to avoid skewed understandings/results from the on-shelf values this section could be commented out if needed 
        ##CHECK THAT THIS IS WORKING PROPERLY!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        #bottom_slice = DS_d.U.isel(z = -1).isel(time_counter = 0)
        #bottom_slice_bool = bottom_slice.notnull()
        #shelf_mask, temp = xr.broadcast(bottom_slice_bool, DS_d.isel(time_counter=0))
        #DS_d = DS_d.where(shelf_mask)
        #print(DS_d)
        #print(DS_d.vosaline[0,20:30,50,:10].to_numpy())
        #shelfMask = DS_d.vosaline.isel(z=-1).isel(time_counter=0).drop_vars(['z','time_counter'])
        #print(shelfMask)

        #masking the shelves, where the bottom slice of salinity (across all times) is above zero instead of nan
        DS_d = DS_d.where(DS_d.vosaline.isel(z=-1).isel(time_counter=0).drop_vars(['z','time_counter'])>0,drop=True)
        #print(DS_d.vosaline[0,20:30,50,:10].to_numpy())
        #print(DS_d)

        #print(DS_d.U[0,:,30,30].to_numpy())
        DS_d['U'] = DS_d.U.mean(dim=['z','time_counter'])
        DS_d['V'] = DS_d.V.mean(dim=['z','time_counter'])
        DS_d = DS_d.drop_vars(['vosaline','z','time_counter'])
        
        DS_d.to_netcdf(run + '_currentVel/' + run + '_avgCurrentVel_map_' + mask_choice + str(d) + '.nc')
        #print(DS_d.U[0,30,30].to_numpy())
        #HC_avg_time.to_netcdf(run + '_heat/' + run + '_HC_timeAvg_' + mask_choice + str(d) + '.nc') 
        #HC_sum_space = HC_sum_deptht.sum(dim=['y_grid_T','x_grid_T'])
        #HC_sum_space.to_netcdf(run + '_heat/' + run + '_HC_spaceSum_' + mask_choice + str(d) + '.nc')

if __name__ == '__main__':
    mask_choice = 'LS' #choose which mask; options are 'LSCR', 'LS2k', or 'LS'
    for run in ['EPM151','EPM152','EPM155','EPM156','EPM157','EPM158']:
        currentVelocity(run,mask_choice)
