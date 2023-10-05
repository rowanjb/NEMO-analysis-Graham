#simple little script for masking the Argo MLD data

import xarray as xr
import numpy as np

#using a random ANHA4 file as a basis for making the masks
filepath = '/home/rowan/projects/rrg-pmyers-ad/pmyers/ANHA4/ANHA4-EPM151-S/ANHA4-EPM151_y2002m05d10_gridT.nc'
testFile = xr.open_dataset(filepath)

Argo = xr.open_dataset('Argo_mixedlayers_monthlyclim_04142022.nc')

###################################################################################################################################################
#MASKING WHERE LABRADOR SEA DEPTH IS LESS THAN 2000m
###################################################################################################################################################

with xr.open_dataarray('mask_LS_2k.nc') as DS:
    mask = DS[:,:,0].astype(int).rename({'deptht':'z','x_grid_T':'x','y_grid_T':'y'})
mask = mask.where(mask>0,drop=True)

ArgoDA = Argo.mld_da_mean

print(ArgoDA)
quit()


###################################################################################################################################################
#MASKING THE ENTIRE LABRADOR SEA
###################################################################################################################################################

with xr.open_dataarray('mask_LS.nc') as DS:
    mask = DS.astype(int)#.rename({'deptht':'z','x_grid_T':'x','y_grid_T':'y'})


###################################################################################################################################################
#MASKING THE LS CONVECTION REGION
###################################################################################################################################################

with xr.open_dataset('ARGOProfiles_mask.nc') as DS:
    mask = DS.tmask.astype(int)

