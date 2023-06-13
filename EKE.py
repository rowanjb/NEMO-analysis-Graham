#exports dataarray of EKE for ANHA4 runs
#Rowan Brown
#May 5, 2023

#figure out a way to not calc EKE too far out of masked area

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

#user specs
run = 'EPM151' #specify the run
window = 5 #specify the rolling window (window = 5 ensures a 25 day window, because it's 5 x 5 files with 5 days per ANHA4 output file)
#(Window might need to be odd, but I'm not sure)
mask_choice = 'LS' #choose which mask; options are 'LSCR', 'LS2k', or 'LS'

#creating directory if doesn't already exist
dir = run + '_EKE/'
if not os.path.exists(dir):
    os.makedirs(dir)

##################################################################################################################
#MASKS

#mask for land, bathymetry, etc. and horiz. grid dimensions
with xr.open_dataset('masks/ANHA4_mesh_mask.nc') as DS:
    tmask = DS.tmask[0,:,:,:].to_numpy() #DataArray with dims (t: 1, z: 50, y: 800, x: 544) 
    e1t = DS.e1t[0,:,:] 
    e2t = DS.e2t[0,:,:]

if mask_choice == 'LS2k': #mask for 2000m depth interior area
    mask = xr.open_dataarray('masks/mask_LS_2k.nc').astype(int).rename({'deptht':'z','x_grid_T':'x','y_grid_T':'y','nav_lat_grid_T':'nav_lat','nav_lon_grid_T':'nav_lon'})
elif mask_choice == 'LS': #mask for entire LS region
    mask = xr.open_dataarray('masks/mask_LS.nc').astype(int).rename({'deptht':'z','x_grid_T':'x','y_grid_T':'y','nav_lat_grid_T':'nav_lat','nav_lon_grid_T':'nav_lon'})
elif mask_choice == 'LSCR': #mask for LS convection region
    mask = xr.open_dataset('masks/ARGOProfiles_mask.nc').tmask.astype(int)
else:
    print("Y'all didn't choose a mask")
    quit()

##################################################################################################################
#OPENING AND INITIAL PROCESSING OF THE NETCDF MODEL OUTPUT FILES

#text files with lists of all non-empty model outputs
#U and V files are needed because U and V velocities determine EKE
#T is needed to get the T-cell depths
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

#preprocessing (specifying desired variables)
preprocess_gridU = lambda ds: ds[['e3u','vozocrtx']]
preprocess_gridV = lambda ds: ds[['e3v','vomecrty']]
preprocess_gridT = lambda ds: ds[['e3t']]

#open the datasets
DSU = xr.open_mfdataset(filepaths_gridU,preprocess=preprocess_gridU,engine="netcdf4")
DSV = xr.open_mfdataset(filepaths_gridV,preprocess=preprocess_gridV,engine="netcdf4")
DST = xr.open_mfdataset(filepaths_gridT,preprocess=preprocess_gridT,engine="netcdf4")

#renaming dimensions so that they are the same for both velocity components
DSU = DSU.rename({'depthu': 'z'})
DSV = DSV.rename({'depthv': 'z'})
DST = DST.rename({'deptht': 'z', 'y_grid_T': 'y', 'x_grid_T': 'x'})

#add horizontal cell dimensions as variables to gridT dataset
DST = DST.assign(e1t=e1t,e2t=e2t)

#masking the general Lab Sea area to save computational expense
northLat = 70
westLon = -70
southLat = 45
eastLon = -35
#DST = DST.where((DST.nav_lat_grid_T < northLat) & (DST.nav_lat_grid_T > southLat) & (DST.nav_lon_grid_T < eastLon) & (DST.nav_lon_grid_T > westLon),drop=True)

DSU = DSU.assign_coords(nav_lat_grid_T=DST.nav_lat_grid_T)#e1t=DST.e1t, e2t=DST.e2t, e3t=DST.e3t)
#DSU = DSU.reset_coords(names=['e1t','e2t','e3t'])
print(DSU)
quit()

#TESTING LINES: are different files' coordinates equal, ie does depthu=depthv? 
#print(DSU.z.to_numpy() - DSV.z.to_numpy())
#print(DSU.z.to_numpy() - mask.z.to_numpy())
#print(DSU.nav_lat[240:250,250].to_numpy() - DSU.nav_lat[240:250,250].to_numpy())
#print(DSU.nav_lat[300:340].to_numpy() - DSV.nav_lat[300:340].to_numpy())
#print(np.sum(DST.nav_lat[300:340].to_numpy() - DSU.nav_lat[300:340].to_numpy()))

##################################################################################################################
#CALCULATIONS

#EKE is calculated based on the methods from: Martínez-Moreno et al. - Global changes in oceanic mesoscale currents over the satellite altimetry record
# => EKE = (1/2) * density_0 * (u'**2 + v'**2) [J/m**3] where u′ = u − u_mean and v′ = v − v_mean
#recall, units are J = kg m**2 / s**2, density = kg / m**3, and vel**2 = m**2 / s**2, so density*vel**2 = kg / m s**2 = J / m**3
#so, integrating  over volume gives total Joules

#first, velocities are co-located on the T grid: 
DSU = DSU.interp(x=DSU.x+0.5)
DSV = DSV.interp(y=DSV.y-0.5)

#re-mapping 'x' and 'y' so they're consistent with the T grid
DSU = DSU.assign_coords(x=DSU.x-0.5)
DSV = DSV.assign_coords(y=DSV.y+0.5)

#EKE calculations
#note that window is specified at the start of the script
rho_0 = 1025 #reference density
DSU_bar_sqr = (DSU-DSU.rolling(time_counter=window,center=True).mean())**2 
DSV_bar_sqr = (DSV-DSV.rolling(time_counter=window,center=True).mean())**2
EKE = (1/2) * rho_0 * (DSU_bar_sqr.vozocrtx + DSV_bar_sqr.vomecrty) #NOTE: resuts in a dataarray
EKE = EKE.rename('EKE')

#add grid T lat and lons as variables (useful for plotting later)
EKE = EKE.assign_coords(e1t=DST.e1t, e2t=DST.e2t, e3t=DST.e3t)
EKE = EKE.reset_coords(names=['e1t','e2t','e3t'])

#apply masks
#NOTE: masks are applied AFTER the EKE calculations because otherwise (I think...) interpolation at the boundaries of the masked regions won't work
EKE.coords['tmask'] = (('z', 'y', 'x'), tmask) #add mask of in-land cells as coords
EKE = EKE.where(EKE.tmask == 1) #drop data outside of mask
if mask_choice == 'LSCR' or mask_choice == 'LS2k' or mask_choice == 'LS': #same as above but with data outside the region of interest
    EKE.coords['mask'] = mask
    EKE = EKE.where(EKE.mask == 1, drop=True)

#dropping unnecessary coordinates (potentially saving memory?)
EKE = EKE.drop_vars('time_centered')
EKE = EKE.drop_vars({'nav_lat','nav_lon'})
#NOTE: nav_lat_grid_T d.n.e. nav_lat, and since things are co-located on the T gird, nav_lat and nav_lon are removed in favour of their grid_T counterparts

#loop through the 4 depths and save .nc files
for d in [50,200,1000,2000]: 
    EKEd = EKE.where(EKE.z < d, drop=True) #creating new dataset truncated at depth d

    #note: there are two main ideas below: "col" refers to the idea that we're looking at column-wise averages, ie so we can make maps later. On 
    #the other hand, "region" refers to region-wise averages, so that we can make time plots later.

    #masking shelves
    #NOTE: bathy is masked to avoid skewed understandings/results from the on-shelf values   
    #this section could be commented out if needed 
    bottom_slice = EKEd.isel(z = -1).isel(time_counter = int(np.floor(window/2))) #slice of dataset at the bottom depth (ie 50m or 200m)
    bottom_slice_bool = bottom_slice.notnull() #making values not in mask equal nan (in-land/shelf values were made nan earlier)
    shelf_mask, temp = xr.broadcast(bottom_slice_bool, EKEd.isel(time_counter=0)) #expanding the mask to the same shape as EKEd (note temp is for temporary)
    EKEd = EKE.where(shelf_mask) #masking EKE (and I guess e1t, e2t, and e3t)
    
    #cell volumes
    volumes = EKEd.e1t*EKEd.e3t*EKEd.e3t
    
    #total Joules in each cell
    EKEd['EKE_per_cell_in_J'] = EKEd.EKE*volumes

    #total Joules in each column
    #NOTE for below: if you're not blocking out shelf values, skipna should be true
    EKEd['EKE_per_column_in_J'] = EKEd.EKE_per_cell_in_J.sum('z',skipna=False) #nans can only by in columns on the shelves, where they're masked, so it's ok and convenient for skipna=False
    EKEd['EKE_per_column_in_J_avg_in_time'] = EKEd.EKE_per_column_in_J.mean('time_counter',skipna=True) #don't include nans in the calculations since they're on days we don't want to include

    #total Joules in the masked region
    EKEd['EKE_in_region_in_J'] = EKEd.EKE_per_cell_in_J.sum(['z','x','y'],skipna=True)

    #saving
    EKEd.EKE_per_column_in_J_avg_in_time.to_netcdf(run + '_EKE/' + run + '_EKE_timeAvg_' + mask_choice + str(d) + '.nc')
    EKEd.EKE_in_region_in_J.to_netcdf(run + '_EKE/' + run + '_EKE_regionAvg_' + mask_choice + str(d) + '.nc')
