import matplotlib.pyplot as plt
import matplotlib.path as mpath
#import datetime
import matplotlib.dates as mdates
import xarray as xr
import os
import numpy as np
import density
#import LSmap

h = 2000 #reference depth
g = 9.80665 #gravity

#list of model .nc output filepaths (e.g. ANHA4 outputs from the EPM151 run)
pauls_nemo_dir = '/home/rowan/projects/rrg-pmyers-ad/pmyers/ANHA4/ANHA4-EPM151-S/'
filepaths = sorted([pauls_nemo_dir + file for file in os.listdir(pauls_nemo_dir) if file.endswith('gridT.nc')])#[0::600]

#horizontal grid variables
with xr.open_dataset('/home/rowan/projects/rrg-pmyers-ad/rowan/ANHA4_mesh_mask.nc') as DS:
    e1t = DS.e1t[0,:,:].rename({'y': 'y_grid_T','x': 'x_grid_T'}) #renames dims
    e2t = DS.e2t[0,:,:].rename({'y': 'y_grid_T','x': 'x_grid_T'})
    lons = np.array(DS.variables['nav_lon'])
    lats = np.array(DS.variables['nav_lat'])

##convective region mask
#with xr.open_dataset('/home/rowan/projects/rrg-pmyers-ad/rowan/ARGOProfiles_mask.nc') as DS:
#    LS_convec_mask = DS.tmask.fillna(0).to_numpy()

#accessing output files
preprocess_gridT = lambda ds: ds[['e3t','votemper','vosaline','somxl010']] #get desired variables only
with xr.open_mfdataset(filepaths,preprocess=preprocess_gridT) as DS:  #,engine='h5netcdf'
    DS = DS.where(DS.deptht < h, drop = True) #drop all depths beyond reference depth (they're uneeded)

#the important variables
T = DS.votemper
S = DS.vosaline
e3t = DS.e3t

areas = np.multiply(e1t,e2t) #area of each cell
Th = T.isel(deptht=-1) #temperature values in the deepest level
Sh = S.isel(deptht=-1) #salinity values in the deepest level

refDens = density.density(Sh,Th) #potential densities at (around) h
dens = density.density(S,T) #densities in each cell from surface to h

#following the equation from "Introducing LAB60..."
term1 = np.multiply(e3t.sum(dim='deptht'),refDens) 
term2 = np.multiply(dens,e3t).sum(dim='deptht')
integrand = np.subtract(term1,term2) 
convE = np.multiply(np.multiply(integrand,areas),np.divide(g,areas))
convE = convE.where(refDens>1000)

##drop data outside mask
#convE.coords['LS_convec_mask'] = (('y_grid_T', 'x_grid_T'), LS_convec_mask) #add mask as coords
#convE = convE.where(convE.LS_convec_mask == 1, drop=True) #drop data outside of mask

#calculating area mean
convEmean = convE.mean(dim=["y_grid_T", "x_grid_T"])
convEmean2 = convEmean.mean(dim="time_counter")
#minmax = 0, 4000 #alternatively, can assign min and max values manually
#
##plotting and saving maps/figures
#CBlabel = 'Convective energy ($J$ $m^{-3}$)'
#title = 'Convective energy (EPM152)'
#fileName  = 'ConvE_pics_EPM152/LS_convective_energy_EPM152_'
#for i,time in enumerate(convE.time_counter):
#    LSmap.LSmap(convE.isel(time_counter=i),lons,lats,minmax,CBlabel,title,fileName)

dates = convEmean.indexes['time_counter'].to_datetimeindex(unsafe=True) #Beware: warning turned off!!
dates = [d.date() for d in dates]
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=800))
plt.plot(dates, convEmean, label = "Convective resistance")
plt.axhline(y=convEmean2, linestyle='--', label = "Long-term mean")
plt.legend()
plt.xticks(rotation=45)
plt.title('Convective resistance in the LS convection region, EPM151')
plt.ylabel('Convective resistance ($J/m^3$)')
plt.xlabel('Time')
plt.savefig('temp-EPM151_ConvE_convectiveRegion.png', dpi=1200, bbox_inches="tight")
