"""Function for getting cell volumes in a non-masked ANHA4 grid.
Basically exists because I didn't want to c+p this code a bunch of times.
Only works for EPM151, 152, 155, 156, 157, and 158
"""

import numpy as np 
import xarray as xr
import os

def volumes(run):
    """Gives cell volumes for the ANHA4 grid.

        Parameters:
            run: run name, i.e., EPM151

        Returns:
            Dataset (or array?) of cell volumes
    """

    run  = str(run)

    #mask for land, bathymetry, etc. to reduce computational cost
    with xr.open_dataset('ANHA4_mesh_mask.nc') as DS:
        tmask = DS.tmask[0,:,:,:].to_numpy() #DataArray with dims (t: 1, z: 50, y: 800, x: 544) 

    #I have text files that list all the non-empty model runs 
    #there is one text file per .nc type, i.e. gridT, gridW, icemod, etc.
    #each run has a folder (e.g. EPM151_filepaths) containing the associated text files
    #the gridV and gridU paths are:
    gridT_txt = run + '_filepaths/' + run + '_gridT_filepaths.txt'

    #open the text files and get lists of the .nc output filepaths
    with open(gridT_txt) as f:
        lines = f.readlines()
    filepaths_gridT = [line.strip() for line in lines]

    #getting horizontal cell dimensions
    with xr.open_dataset('ANHA4_mesh_mask.nc') as DS:
        e1t = DS.e1t[0,:,:].rename({'y': 'y_grid_T','x': 'x_grid_T'}) #renames dims
        e2t = DS.e2t[0,:,:].rename({'y': 'y_grid_T','x': 'x_grid_T'}) #note first dim is t:1

    #getting vertical cell dimensions
    preprocess_gridT = lambda ds: ds[['e3t']]
    DS = xr.open_mfdataset(filepaths_gridT,preprocess=preprocess_gridT)#[:-2],data_vars='minimal',coords='minimal',preprocess=preprocess_gridT)

    #joining cell dimensions
    DS[['e1t','e2t']] = e1t,e2t #add T cell dimensions as variables

    #volumes dataarray
    volumes = DS.e1t*DS.e3t*DS.e2t 

    ##mask LS convection region
    #with xr.open_dataset('ARGOProfiles_mask.nc') as DS:
    #    LS_convec_mask = DS.tmask.fillna(0).to_numpy()
    #volumes.coords['LS_convec_mask'] = (('y_grid_T', 'x_grid_T'), LS_convec_mask) #add mask as coords
    #volumes = volumes.where(volumes.LS_convec_mask == 1, drop=True) #drop data outside of mask

    ##save the volumes dataarray
    #volumes.to_netcdf('volumes_' + run + '_LSCR.nc')

    return volumes
