#Looks at the forcing sets
#Rowan Brown
#17 Sept 2023

import numpy as np 
import xarray as xr
import os

def air(run,mask_choice):
   
    #creating directory if doesn't already exist
    dir = run + '_air/'
    if not os.path.exists(dir):
        os.makedirs(dir)
    
    ##################################################################################################################
    #OPENING AND INITIAL PROCESSING OF THE NETCDF MODEL OUTPUT FILES

    #these are text files with lists of all non-empty model outputs (made with 'filepaths.py')
    ##gridU_txt = run + '_filepaths/' + run + '_gridU_filepaths.txt'
    ##gridV_txt = run + '_filepaths/' + run + '_gridV_filepaths.txt'
    ##gridT_txt = run + '_filepaths/' + run + '_gridT_filepaths.txt'
    icemod_txt = run + '_filepaths/' + run + '_icemod_filepaths.txt'

    #open the text files and get lists of the .nc output filepaths
    ##with open(gridU_txt) as f: lines = f.readlines()
    ##filepaths_gridU = [line.strip() for line in lines][:3]
    ##with open(gridV_txt) as f: lines = f.readlines()
    ##filepaths_gridV = [line.strip() for line in lines][:3]
    ##with open(gridT_txt) as f: lines = f.readlines()
    ##filepaths_gridT = [line.strip() for line in lines][:3]
    with open(icemod_txt) as f: lines = f.readlines()
    filepaths_icemod = [line.strip() for line in lines]

    #preprocessing (specifying variables that we need and ignoring the rest)
    ##preprocess_gridU = lambda ds: ds[['sozotaux']] #sozotaux {'standard_name': 'surface_downward_x_stress', 'long_name': 'Wind Stress along i-axis', 'units': 'N/m2' ... }
    ##preprocess_gridV = lambda ds: ds[['sometauy']] #sometauy {'standard_name': 'surface_downward_y_stress', 'long_name': 'Wind Stress along j-axis', 'units': 'N/m2' ... } 
    ##preprocess_gridT = lambda ds: ds[['votemper','vosaline']]
    preprocess_icemod = lambda ds: ds[['sohefldo']]  #sohefldo {'standard_name': 'surface_downward_heat_flux_in_sea_water', 'long_name': 'Net Downward Heat Flux', 'units': 'W/m2' ... }

    #open the datasets
    ##DSU = xr.open_mfdataset(filepaths_gridU,preprocess=preprocess_gridU,engine="netcdf4")
    ##DSV = xr.open_mfdataset(filepaths_gridV,preprocess=preprocess_gridV,engine="netcdf4")
    ##DST = xr.open_mfdataset(filepaths_gridT,preprocess=preprocess_gridT,engine="netcdf4")
    DSICE = xr.open_mfdataset(filepaths_icemod,preprocess=preprocess_icemod,engine="netcdf4")

    #renaming dimensions so that they are the same for all datasets
    ##DSU = DSU.rename({'depthu': 'z'})
    ##DSV = DSV.rename({'depthv': 'z'})
    ##DST = DST.rename({'deptht': 'z', 'y_grid_T': 'y', 'x_grid_T': 'x'})

    ##################################################################################################################
    #MASKS

    #mask for land, bathymetry, etc. and horiz. grid dimensions
    #check this to be sure, but I'm pretty sure these masks are made redudant by the other masks
    with xr.open_dataset('masks/ANHA4_mesh_mask.nc') as DS:
        #DST = DST.assign_coords(tmask=DS.tmask[0,:,:,:])
        #DSU = DSU.assign_coords(umask=DS.umask[0,:,:,:])
        #DSV = DSV.assign_coords(vmask=DS.vmask[0,:,:,:])
        DSICE['e1t'] = DS.e1t[0,:,:] 
        DSICE['e2t'] = DS.e2t[0,:,:]
        #WHAT GRID IS THE ICEMOD FILE ON?

    if mask_choice == 'LS2k': 
        with xr.open_dataarray('masks/mask_LS_2k.nc') as DS:
            DSICE = DSICE.assign_coords(mask=DS[:,:,0].astype(int).rename({'x_grid_T':'x','y_grid_T':'y'}))
    elif mask_choice == 'LS': 
        with xr.open_dataarray('masks/mask_LS.nc') as DS:
            DSICE = DSICE.assign_coords(mask=DS[:,:,0].astype(int).rename({'x_grid_T':'x','y_grid_T':'y'}))
    elif mask_choice == 'LSCR': 
        with xr.open_dataset('masks/ARGOProfiles_mask.nc') as DS:
            DSICE = DSICE.assign_coords(mask = DS.tmask.astype(int))
    else:
        print("Y'all didn't choose a mask")
        quit()

    #apply general mask around the LS (I assume this saves computational power when doing the later calculations?)
    ##DST = DST.where((DST.x>100)&(DST.x<250)&(DST.y>300)&(DST.y<500),drop=True)
    ##DSU = DSU.where((DSU.x>100)&(DSU.x<250)&(DSU.y>300)&(DSU.y<500),drop=True)
    ##DSV = DSV.where((DSV.x>100)&(DSV.x<250)&(DSV.y>300)&(DSV.y<500),drop=True)
    ##DSICE = DSICE.where((DSICE.x>100)&(DSICE.x<250)&(DSICE.y>300)&(DSICE.y<500),drop=True)

    ##################################################################################################################
    #FLUX CALCULATIONS

    #masking
    DSICE = DSICE.where(DSICE.mask == 1, drop=True)

    #total flux in each cell
    DSICE['heat_flux_in_each_cell'] = DSICE.sohefldo*DSICE.e1t*DSICE.e2t #[W]

    #saving
    DSICE['heat_flux_map'] = DSICE.heat_flux_in_each_cell.mean(dim='time_counter')
    DSICE.heat_flux_map.to_netcdf(run + '_air/' + run + '_air_map_' + mask_choice + '.nc')
    DSICE['heat_flux_timeplot'] = DSICE.heat_flux_in_each_cell.sum(dim=['x','y'])
    DSICE.heat_flux_timeplot.to_netcdf(run + '_air/' + run + '_air_timeplot_' + mask_choice + '.nc')

if __name__ == '__main__':
    for i in ['EPM157','EPM158']:
        air(run=i,mask_choice='LS2k')
        air(run=i,mask_choice='LS')
        #for j in ['LS2k','LS','LSCR']:
            #air(run=i,mask_choice=j)

