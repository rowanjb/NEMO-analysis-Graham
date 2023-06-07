#exports dataarray of EKE for ANHA4 runs
#Rowan Brown
#May 5, 2023

import numpy as np 
import xarray as xr
import os

#user specs
run = 'EPM157' #specify the run
window = 3 #specify the rolling window
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
    e1t = DS.e1t[0,:,:]#.rename({'y': 'y_grid_T','x': 'x_grid_T'}) #renames dims
    e2t = DS.e2t[0,:,:]#.rename({'y': 'y_grid_T','x': 'x_grid_T'})

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
gridU_txt = run + '_filepaths/' + run + '_gridU_filepaths.txt'
gridV_txt = run + '_filepaths/' + run + '_gridV_filepaths.txt'
gridT_txt = run + '_filepaths/' + run + '_gridT_filepaths.txt'

#open the text files and get lists of the .nc output filepaths
with open(gridU_txt) as f: lines = f.readlines()
filepaths_gridU = [line.strip() for line in lines][:3]
with open(gridV_txt) as f: lines = f.readlines()
filepaths_gridV = [line.strip() for line in lines][:3]
with open(gridT_txt) as f: lines = f.readlines() #needed for e3t and later calculation of cell volumes
filepaths_gridT = [line.strip() for line in lines][:3]

#preprocessing
preprocess_gridU = lambda ds: ds[['e3u','vozocrtx']] #desired variables
preprocess_gridV = lambda ds: ds[['e3v','vomecrty']] #desired variables
preprocess_gridT = lambda ds: ds[['e3t']] #desired variable

#open the datasets
DSU = xr.open_mfdataset(filepaths_gridU,preprocess=preprocess_gridU,engine="netcdf4") #opens dataset
DSV = xr.open_mfdataset(filepaths_gridV,preprocess=preprocess_gridV,engine="netcdf4") #opens dataset
DST = xr.open_mfdataset(filepaths_gridT,preprocess=preprocess_gridT,engine="netcdf4") #opens dataset

#renaming dimensions so that they are the same for both velocity components
DSU = DSU.rename({'depthu': 'z'})  
DSV = DSV.rename({'depthv': 'z'}) 
DST = DST.rename({'deptht': 'z', 'y_grid_T': 'y', 'x_grid_T': 'x'})#, 'nav_lat_grid_T': 'nav_lat', 'nav_lon_grid_T': 'nav_lon'})

#add horizontal cell dimensions
DST = DST.assign(e1t=e1t,e2t=e2t)#_coords(e1t=e1t, e2t=e2t)

#are different files' coordinates equal, ie does depthu=depthv? 
#print(DSU.z.to_numpy() - DSV.z.to_numpy())
#print(DSU.z.to_numpy() - mask.z.to_numpy())
#print(DSU.nav_lat[240:250,250].to_numpy() - DSU.nav_lat[240:250,250].to_numpy())
#print(DSU.nav_lat[300:340].to_numpy() - DSV.nav_lat[300:340].to_numpy())
#print(np.sum(DST.nav_lat[300:340].to_numpy() - DSU.nav_lat[300:340].to_numpy()))

##apply tmask
#DSV.coords['tmask'] = (('z', 'y', 'x'), tmask) #add mask as coords
#DSV = DSV.where(DSV.tmask == 1) #drop data outside of mask
#DSU.coords['tmask'] = (('z', 'y', 'x'), tmask) #add mask as coords
#DSU = DSU.where(DSU.tmask == 1) #drop data outside of mask
#DST.coords['tmask'] = (('z', 'y', 'x'), tmask)
#DST = DST.where(DST.tmask == 1)

##apply mask (if there is one)
##wait, this should be below the calculation section####################################################
#if mask_choice == 'LSCR' or mask_choice == 'LS2k' or mask_choice == 'LS':
#    DSU.coords['mask'] = mask
#    DSU = DSU.where(DSU.mask == 1, drop=True)
#    DSV.coords['mask'] = mask
#    DSV = DSV.where(DSV.mask == 1, drop=True)
#    DST.coords['mask'] = mask
#    DST = DST.where(DST.mask == 1, drop=True)

##################################################################################################################
#want to output:
# - EKE in the columns for all 4 depths across time for mapping purposes (all time???? or equal time windows) 
# - total EKE in masked region for all 4 depths for plotting in time (all time???? or equal time windows) 
##################################################################################################################
#CALCULATIONS

#co-locate the velocities onto the T grid 
DSU = DSU.interp(x=DSU.x+0.5)
DSV = DSV.interp(y=DSV.y-0.5)

#re-mapping x and y so they're consistent with the T grid
DSU = DSU.assign_coords(x=DSU.x-0.5)
DSV = DSV.assign_coords(y=DSV.y+0.5)

#EKE is calculated based on the methods from: Martínez-Moreno et al. - Global changes in oceanic mesoscale currents over the satellite altimetry record
# => EKE = (1/2) * density_0 * (u'**2 + v'**2) [J/m**3] where u′ = u − u_mean and v′ = v − v_mean
#recall, units are J = kg m**2 / s**2, density = kg / m**3, and vel**2 = m**2 / s**2, so density*vel**2 = kg / m s**2 = J / m**3
#so, integrating this forumation of EKE over volume gives total Joules

#EKE calculations (ensure window=5 for actual calculations)
rho_0 = 1025 #density
DSU_bar_sqr = (DSU-DSU.rolling(time_counter=window,center=True).mean())**2 
DSV_bar_sqr = (DSV-DSV.rolling(time_counter=window,center=True).mean())**2
EKE = (1/2) * rho_0 * (DSU_bar_sqr.vozocrtx + DSV_bar_sqr.vomecrty) #resuts in a dataArray
EKE = EKE.rename('EKE')

#add grid T lat and lons (useful for later plotting) ####and drop values outside the Labrador Sea 
EKE = EKE.assign_coords(e1t=DST.e1t, e2t=DST.e2t, e3t=DST.e3t)
EKE = EKE.reset_coords(names=['e1t','e2t','e3t'])

#apply masks
EKE.coords['tmask'] = (('z', 'y', 'x'), tmask) #add mask as coords
EKE = EKE.where(EKE.tmask == 1) #drop data outside of mask
if mask_choice == 'LSCR' or mask_choice == 'LS2k' or mask_choice == 'LS':
    EKE.coords['mask'] = mask
    EKE = EKE.where(EKE.mask == 1, drop=True)

#dropping unnecessary coordinate (saving memory?)
EKE = EKE.drop_vars('time_centered')
#NOTE: nav_lat_grid_T d.n.e. nav_lat, and since things are co-located on the t grid, I think we should remove nav_lat and nav_lon
EKE = EKE.drop_vars({'nav_lat','nav_lon'})

#don't need to mask values out of LS when you're already applying an LS mask...
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

#loop through the 4 depths and save .nc files
for d in [50,200,1000,2000]: 

    #note: there are two main ideas below: "col" refers to the idea that we're looking at water-columnwise averages, ie so we can make maps later. On 
    #the other hand, "region" refers to regionwise averages, so that we can make time plots later.

    #masking shelves
    #note: you need to mask the bathy or else the on-shelf values/averages/weights will be messed up. But really, you shouldn't include these
    #areas at all because on-shelf averages will be more extreme than in deeper areas and it'll through your visuals off.
    EKEd = EKE.where(EKE.z < d, drop=True) #drop values below specified depth
    #########print(EKEd[1,10:25,60,40:55].to_numpy())
    bottom_slice = EKEd.isel(z = -1).isel(time_counter = int((window-1)/2)) #time counter should be a random non-nan day
    #print(bottom_slice[60,30:45].to_numpy()) #these coordinates show a section inc. a shelf, and it can be checked that this area is then deleted
    bottom_slice_bool = bottom_slice.notnull() #in-land/shelf values were made nan earlier
    shelf_mask, temp = xr.broadcast(bottom_slice_bool, EKEd.isel(time_counter=0)) #temp is temporary
    EKEd = EKE.where(shelf_mask)# keep_attrs=True)
    #########print(EKEd[1,10:25,60,40:55].to_numpy())
    
    #cell volumes
    volumes = EKEd.e1t*EKEd.e3t*EKEd.e3t
    
    #total Joules in each cell
    EKEd['EKE_per_cell_in_J'] = EKEd.EKE*volumes

    #total Joules in each column
    EKEd['EKE_per_column_in_J'] = EKEd.EKE_per_cell_in_J.sum('z',skipna=False) #nans are only in columns on the shelves, where they're masked, so it's ok and convenient for skipna=False
    EKEd['EKE_per_column_in_J_avg_in_time'] = EKEd.EKE_per_column_in_J.mean('time_counter',skipna=True) #don't include nans in the calculations since they're on days we don't want to include

    #total Joules in the masked region
    EKEd['EKE_in_region_in_J'] = EKEd.EKE_per_cell_in_J.sum(['z','x','y'],skipna=True)

    #saving
    EKEd.EKE_per_column_in_J_avg_in_time.to_netcdf(run + '_EKE/' + run + '_EKE_timeAvg_' + mask_choice + str(d) + '.nc')
    EKEd.EKE_in_region_in_J.to_netcdf(run + '_EKE/' + run + '_EKE_regionAvg_' + mask_choice + str(d) + '.nc')
    

    quit()


    volumes = EKEd.e1t*EKEd.e3t*EKEd.e3t #volume of each cell
    avg_col_vol = volumes.mean(dim='z') #average cell volume in each column
    weights = volumes/avg_col_vol #dataarray of weights
    weights = weights.fillna(0)
    EKE_col_weighted = EKEd.EKE.weighted(weights)
    EKE_avg_col = EKE_col_weighted.mean('z')
    EKE_avg_col_time = EKE_avg_col.mean(dim='time_counter')
    EKE_avg_col_time.to_netcdf(run + '_EKE/' + run + '_EKE_timeAvg_' + mask_choice + str(d) + '.nc') #.nc with time-avg temp in each column (ie for making maps)

    avg_cell_vol = volumes.mean(dim=['z','y','x'])
    weights = volumes/avg_cell_vol
    weights = weights.fillna(0)
    EKE_region_weighted = EKEd.EKE.weighted(weights)
    EKE_avg_region = EKE_region_weighted

    quit()

    EKE = EKE.sum(dim='z') #summing in z direction
    EKE = EKE.mean(dim='time_counter') #taking average in time
    EKE.to_netcdf('EKE/EKE_avg_' + run + '_' + str(maxDepth) + '_incShelf.nc') #saving
    
    #temperature averaged through time
    #cell weights (col): divide cell volume by average cell volume in each column
    volumes = DS_d.e1t*DS_d.e3t*DS_d.e2t #volume of each cell
    #print('vol at depth 2: ' + str(volumes[10,10,0,2].to_numpy()))
    #print('vol at depth 30: ' + str(volumes[10,10,0,30].to_numpy()))
    avg_col_vol = volumes.mean(dim='deptht') #average cell volume in each column
    #print('vol of col total: ' + str(avg_col_vol[10,10,0].to_numpy()))
    weights = volumes/avg_col_vol #dataarray of weights
    #print('weight of depth 2: ' + str(weights[10,10,0,2].to_numpy()))
    #print('weight of depth 30: ' + str(weights[10,10,0,30].to_numpy()))
    DS_d['votemper_col_weighted'] = DS_d.votemper.weighted(weights)
    DS_d['votemper_avg_col'] = DS_d.votemper_col_weighted.mean(dim='deptht')
    DS_d['votemper_avg_col_time'] = DS_d.votemper_avg_col.mean(dim='time_counter')
    DS_d.votemper_avg_col_time.to_netcdf(run + '_EKE/' + run + '_EKE_timeAvg_' + mask_choice + str(d) + '.nc') #.nc with time-avg temp in each column (ie for making maps)


    #temperature averaged in space
    #cell weights (region): divide cell volume by average cell volume in the whole masked region
    avg_cell_vol = volumes.mean(dim=['deptht','y_grid_T','x_grid_T'])
    weights = volumes/avg_cell_vol
    DS_d['votemper_region_weighted'] = DS_d.votemper.weighted(weights)
    DS_d['votemper_avg_region'] = DS_d.votemper_region_weighted.mean(dim=['deptht','y_grid_T','x_grid_T'])
    DS_d.votemper_avg_region.to_netcdf(run + '_heat/' + run + '_votemper_spaceAvg_' + mask_choice + str(d) + '.nc') #.nc with region-avg temp through time (ie for making time plots)

    ##temperature
    #DS_d['votemper_avg_deptht'] = DS_d.votemper.mean(dim='deptht')
    #DS_d['votemper_avg_time'] = DS_d.votemper_avg_deptht.mean(dim='time_counter')
    #DS_d.votemper_avg_time.to_netcdf(run + '_heat/' + run + '_votemper_timeAvg_' + mask_choice + str(d) + '.nc') #.nc with time-avg temp in each column (ie for making maps)
    #DS_d['votemper_avg_space'] = DS_d.votemper_avg_deptht.mean(dim=['y_grid_T','x_grid_T'])
    #DS_d.votemper_avg_space.to_netcdf(run + '_heat/' + run + '_votemper_spaceAvg_' + mask_choice + str(d) + '.nc') #.nc with region-avg temp through time (ie for making time plots)
    ##DS_d.votemper_avg_deptht.to_netcdf('heat/votemper_' + run + '_' + str(d) + '.nc')

    #heat content
    DS_d['volT'] = DS_d.e1t*DS_d.e3t*DS_d.e2t #volumes of T cells (IS THIS A LEGITIMATE WAY OF MULTIPLYING??????)
    DS_d['HC'] = rho_0 * C_p * 10**(-12) * (DS.votemper - refT) * DS_d.volT  #should be T-Tref, i.e.,  minus??????????????????????????
    DS_d['HC_sum_deptht'] = DS_d.HC.sum(dim='deptht')
    DS_d['HC_avg_time'] = DS_d.HC_sum_deptht.mean(dim='time_counter')
    DS_d.HC_avg_time.to_netcdf(run + '_heat/' + run + '_HC_timeAvg_' + mask_choice + str(d) + '.nc') #.nc with time-avg total HC in each column (ie for making maps)
    DS_d['HC_sum_space'] = DS_d.HC_sum_deptht.sum(dim=['y_grid_T','x_grid_T'])
    DS_d.HC_sum_space.to_netcdf(run + '_heat/' + run + '_HC_spaceSum_' + mask_choice + str(d) + '.nc') #.nc with region-sum HC through time (ie for making time plots)
    #DS_d.HC_sum.to_netcdf('heat/HC_' + run + '_' + str(d) + '.nc')
