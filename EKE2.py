#exports dataarray of EKE for ANHA4 runs
#Rowan Brown
#May 5, 2023

#outputs 8 netcdf files per run (and you get to choose one mask per run):
# - 4 x depths (50m, 200m, 1000m, 2000m)
# - 2 x output data types:
#   - EKE in each column averaged across time, for mapping purposes (should this be updated so that the window can be spec'ed?) 
#   - total EKE in the masked region, for plotting in time

#NOTE: EKE calculations are based off the supplementary material from:
#Martínez-Moreno et al. - Global changes in oceanic mesoscale currents over the satellite altimetry record

import numpy as np 
import xarray as xr
import os

#@profile
def temporary_EKE_function():
    
    #user specs
    run = 'EPM158' 
    window = 5
    mask_choice = 'LS'
    #d = 2000 

    #creating directory if doesn't already exist
    dir = run + '_EKE/'
    if not os.path.exists(dir):
        os.makedirs(dir)
    
    ##################################################################################################################
    #OPENING AND INITIAL PROCESSING OF THE NETCDF MODEL OUTPUT FILES

    #these are text files with lists of all non-empty model outputs (made with 'filepaths.py')
    gridU_txt = run + '_filepaths/' + run + '_gridU_filepaths.txt'
    gridV_txt = run + '_filepaths/' + run + '_gridV_filepaths.txt'
    gridT_txt = run + '_filepaths/' + run + '_gridT_filepaths.txt'

    #open the text files and get lists of the .nc output filepaths
    with open(gridU_txt) as f: lines = f.readlines()
    filepaths_gridU = [line.strip() for line in lines][:3]
    with open(gridV_txt) as f: lines = f.readlines()
    filepaths_gridV = [line.strip() for line in lines][:3]
    with open(gridT_txt) as f: lines = f.readlines()
    filepaths_gridT = [line.strip() for line in lines][:3]

    #preprocessing (specifying variables that we need and ignoring the rest)
    preprocess_gridU = lambda ds: ds[['vozocrtx']]
    preprocess_gridV = lambda ds: ds[['vomecrty']]
    preprocess_gridT = lambda ds: ds[['e3t']]

    #open the datasets
    DSU = xr.open_mfdataset(filepaths_gridU,preprocess=preprocess_gridU,engine="netcdf4")
    DSV = xr.open_mfdataset(filepaths_gridV,preprocess=preprocess_gridV,engine="netcdf4")
    DST = xr.open_mfdataset(filepaths_gridT,preprocess=preprocess_gridT,engine="netcdf4")

    #renaming dimensions so that they are the same for all datasets
    DSU = DSU.rename({'depthu': 'z'})
    DSV = DSV.rename({'depthv': 'z'})
    DST = DST.rename({'deptht': 'z', 'y_grid_T': 'y', 'x_grid_T': 'x'})

    ##################################################################################################################
    #MASKS

    #mask for land, bathymetry, etc. and horiz. grid dimensions
    #check this to be sure, but I'm pretty sure these masks are made redudant by the other masks
    with xr.open_dataset('masks/ANHA4_mesh_mask.nc') as DS:
        #DST = DST.assign_coords(tmask=DS.tmask[0,:,:,:])
        #DSU = DSU.assign_coords(umask=DS.umask[0,:,:,:])
        #DSV = DSV.assign_coords(vmask=DS.vmask[0,:,:,:])
        DST['e1t'] = DS.e1t[0,:,:] 
        DST['e2t'] = DS.e2t[0,:,:]

    if mask_choice == 'LS2k': 
        with xr.open_dataarray('masks/mask_LS_2k.nc') as DS:
            DST = DST.assign_coords(mask=DS.astype(int).rename({'deptht':'z','x_grid_T':'x','y_grid_T':'y'}))
    elif mask_choice == 'LS': 
        with xr.open_dataarray('masks/mask_LS.nc') as DS:
            DST = DST.assign_coords(mask=DS.astype(int).rename({'deptht':'z','x_grid_T':'x','y_grid_T':'y'}))
    elif mask_choice == 'LSCR': 
        with xr.open_dataset('masks/ARGOProfiles_mask.nc') as DS:
            DST = DST.assign_coords(mask = DS.tmask.astype(int))
    else:
        print("Y'all didn't choose a mask")
        quit()

    #apply general mask around the LS
    DST = DST.where((DST.x>100)&(DST.x<250)&(DST.y>300)&(DST.y<500),drop=True)
    DSU = DSU.where((DSU.x>100)&(DSU.x<250)&(DSU.y>300)&(DSU.y<500),drop=True)
    DSV = DSV.where((DSV.x>100)&(DSV.x<250)&(DSV.y>300)&(DSV.y<500),drop=True)

    ##################################################################################################################
    #EKE CALCULATIONS

    #EKE is calculated based on the methods from: Martínez-Moreno et al. - Global changes in oceanic mesoscale currents over the satellite altimetry record
    # => EKE = (1/2) * density_0 * (u'**2 + v'**2) [J/m**3] where u′ = u − u_mean and v′ = v − v_mean
    #recall, units are J = kg m**2 / s**2, density = kg / m**3, and vel**2 = m**2 / s**2, so density*vel**2 = kg / m s**2 = J / m**3
    #so, integrating  over volume gives total Joules

    #first, velocities are co-located on the T grid:
    DSU = DSU.interp(x=DSU.x+0.5).drop_vars('x')
    DSV = DSV.interp(y=DSV.y-0.5).drop_vars('y')

    print(DSV)
    quit()

    #EKE calculations
    rho_0 = 1025
    DSU_bar_sqr = (DSU-DSU.rolling(time_counter=window,center=True).mean())**2 
    DSV_bar_sqr = (DSV-DSV.rolling(time_counter=window,center=True).mean())**2
    EKE = (1/2) * rho_0 * (DSU_bar_sqr.vozocrtx + DSV_bar_sqr.vomecrty) 
    EKE = EKE.rename('EKE')

    #add grid T lat and lons as variables (useful for plotting later)
    EKE = EKE.assign_coords(nav_lat_grid_T=DST.nav_lat_grid_T, nav_lon_grid_T=DST.nav_lon_grid_T,mask=DST.mask,e1t=DST.e1t,e2t=DST.e2t,e3t=DST.e3t)
    EKE = EKE.reset_coords(names=['e1t','e2t','e3t'])

    #apply masks
    EKE = EKE.where(EKE.mask == 1, drop=True)

    #EKE in each cell
    EKE['EKE'] = EKE.EKE * EKE.e1t*EKE.e2t*EKE.e3t #EKE.EKE was originally in units J/m**3, so multiply by volue

    for d in [2000, 1000, 200, 50]:

        #masking below a chosen depth 
        EKE = EKE.where(EKE.z < d, drop=True)
    
        #masking the shelves, where the bottom slice of EKE (across all times) is above zero instead of nan
        #it mightn't ne necessary to mask the shelves, since EKE is summed, not averaged in depth
        EKEd = EKE.where(EKE.EKE.isel(z=-1).isel(time_counter=2).drop_vars(['z','time_counter'])>0,drop=True)

        #final calculations
        EKEd['EKE_per_column_in_J'] = EKEd.EKE.sum(dim='z',skipna=True)
        EKEd['EKE_per_column_in_J_avg_in_time'] = EKEd.EKE_per_column_in_J.mean(dim='time_counter',skipna=True)
        EKEd.EKE_per_column_in_J_avg_in_time.to_netcdf(run + '_EKE/' + run + '_EKE_map_' + mask_choice + str(d) + '.nc') 
        EKEd['EKE_in_region_in_J'] = EKEd.EKE.sum(['z','x','y'],skipna=True)
        EKEd.EKE_in_region_in_J.to_netcdf(run + '_EKE/' + run + '_EKE_timePlot_' + mask_choice + str(d) + '.nc')

if __name__ == '__main__':
    temporary_EKE_function()

