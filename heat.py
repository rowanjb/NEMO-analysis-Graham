import numpy as np 
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import datetime
import matplotlib.dates as mdates
import os

pauls_nemo_dir = '/home/rowan/projects/rrg-pmyers-ad/pmyers/ANHA4/ANHA4-EPM155-S/'
filepaths = sorted([pauls_nemo_dir + file for file in os.listdir(pauls_nemo_dir) if file.endswith('gridT.nc')])#[0::600]

with xr.open_dataset('ANHA4_mesh_mask.nc') as DS:
    e1t = DS.e1t[0,:,:].rename({'y': 'y_grid_T','x': 'x_grid_T'}) #renames dims
    e2t = DS.e2t[0,:,:].rename({'y': 'y_grid_T','x': 'x_grid_T'})
    lons = np.array(DS.variables['nav_lon'])
    lats = np.array(DS.variables['nav_lat'])

with xr.open_dataset('ARGOProfiles_mask.nc') as DS:
    LS_convec_mask = DS.tmask.fillna(0).to_numpy()

preprocess_gridT = lambda ds: ds[['e3t','votemper']]
DS = xr.open_mfdataset(filepaths[:-2],concat_dim='time_counter',data_vars='minimal',coords='minimal',preprocess=preprocess_gridT)

DS[['e1t','e2t']] = e1t,e2t #add T cell dimensions as variables
DS.coords['LS_convec_mask'] = (('y_grid_T', 'x_grid_T'), LS_convec_mask) #add mask as coords
DS = DS.where(DS.LS_convec_mask == 1, drop=True) #drop data outside of mask

refT = -1.8 #reference temperature [C]                              (Value from Paul's email)
rho_0 = 1026#1025 #density reference (const. value?( [kg/m^3]       (Value from Gillard paper)
C_p = 3992#3850 #specific heat capacity (const. value?) [J/kgK]     (Value from Gillard paper)

for d in [50, 200, 1000, 2000]: #loop through depths

    #volumes
    DS_d = DS.where(DS.deptht < d, drop=True) #drop values below specified depth
    DS_d['volT'] = DS_d.e1t*DS_d.e3t*DS_d.e2t #volumes of T cells
    DS_d['volT_total'] = DS_d.volT.sum(dim=['x_grid_T','y_grid_T','deptht']) #volume of region

    #temperatures
    DS_d['votemper_weighted'] = DS_d.volT*DS_d.votemper #weighted temps
    avgT = DS_d.votemper_weighted.sum(dim=['x_grid_T','y_grid_T','deptht'])/DS_d.volT_total #average temperature
    DS['avgT'+str(d)] = avgT

    #heat content (following integral)
    HC_integrand = (DS.votemper+refT)*DS_d.volT
    HC_integral = HC_integrand.sum(dim=['x_grid_T','y_grid_T','deptht'])#/DS_d.volT_total #average adjusted temperature
    DS['HC'+str(d)] = rho_0 * C_p * 10**(-12) * HC_integral

dates = DS.indexes['time_counter'].to_datetimeindex(unsafe=True) #Beware: warning turned off!!
dates = [d.date() for d in dates]
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=800)) 
plt.plot(dates, DS.HC50, label = "Top ~50m") 
plt.plot(dates, DS.HC200, label = "Top ~200m")
plt.plot(dates, DS.HC1000, label = "Top ~1000m")
plt.plot(dates, DS.HC2000, label = "Top ~2000m")
plt.legend()
plt.xticks(rotation=45)
plt.title('Heat content in the LS convection region, EPM155')
plt.ylabel('Heat content (TJ)')
plt.xlabel('Time')
plt.savefig('temp-EPM155_HC_convectiveRegion.png', dpi=1200, bbox_inches="tight")
plt.close()

dates = DS.indexes['time_counter'].to_datetimeindex(unsafe=True) #Beware: warning turned off!!
dates = [d.date() for d in dates]
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=800))
plt.plot(dates, DS.avgT50, label = "Top ~50m")
plt.plot(dates, DS.avgT200, label = "Top ~200m")
plt.plot(dates, DS.avgT1000, label = "Top ~1000m")
plt.plot(dates, DS.avgT2000, label = "Top ~2000m")
plt.legend()
plt.xticks(rotation=45)
plt.title('Average surface temperature in the LS convection region, EPM155')
plt.ylabel('Temperature (degrees Celsius)')
plt.xlabel('Time')
plt.savefig('temp-EPM155_Temperature_convectiveRegion.png', dpi=1200, bbox_inches="tight")
plt.close()
