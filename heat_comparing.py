import numpy as np 
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import datetime
import matplotlib.dates as mdates
import os

pauls_nemo_dir = ['/home/rowan/projects/rrg-pmyers-ad/pmyers/ANHA4/ANHA4-EPM151-S/','/home/rowan/projects/rrg-pmyers-ad/pmyers/ANHA4/ANHA4-EPM155-S/']

for count,i in enumerate(pauls_nemo_dir):

    run = i[-6:-3]
    
    filepaths = sorted([i + file for file in os.listdir(i) if file.endswith('gridT.nc')])#[0::100]

    with xr.open_dataset('ANHA4_mesh_mask.nc') as DS:
        e1t = DS.e1t[0,:,:].rename({'y': 'y_grid_T','x': 'x_grid_T'}) #renames dims
        e2t = DS.e2t[0,:,:].rename({'y': 'y_grid_T','x': 'x_grid_T'})
        lons = np.array(DS.variables['nav_lon'])
        lats = np.array(DS.variables['nav_lat'])

    with xr.open_dataset('ARGOProfiles_mask.nc') as DS:
        LS_convec_mask = DS.tmask.fillna(0).to_numpy()

    preprocess_gridT = lambda ds: ds[['e3t','votemper']]
    DS = xr.open_mfdataset(filepaths[:-2],data_vars='minimal',coords='minimal',preprocess=preprocess_gridT)

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

    if count == 0:
        DS151 = DS
    elif count == 1:
        DS155 = DS

dates151 = DS151.indexes['time_counter'].to_datetimeindex(unsafe=True) #Beware: warning turned off!!
dates151 = [d.date() for d in dates151]
dates155 = DS155.indexes['time_counter'].to_datetimeindex(unsafe=True) #Beware: warning turned off!!
dates155 = [d.date() for d in dates155]

#plt.rc('text', usetex=True)
#plt.rc('font', family='serif')

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))#'%m/%d/%Y'
plt.gca().xaxis.set_major_locator(mdates.YearLocator(base=2)) 

#plt.plot(dates151, DS151.HC50, label = "EPM151, top ~50m", color='blue') 
#plt.plot(dates151, DS151.HC200, label = "EPM151, top ~200m", color='orange')
#plt.plot(dates151, DS151.HC1000, label = "EPM151, top ~1000m", color='green')
plt.scatter(dates151, DS151.HC2000, marker='.', label = "EPM151, top ~2000m",s=0.5)#, color='red')
#plt.plot(dates155, DS155.HC50, label = "EPM155, top ~50m", color='blue', linestyle='dashed')
#plt.plot(dates155, DS155.HC200, label = "EPM155, top ~200m", color='orange', linestyle='dashed')
#plt.plot(dates155, DS155.HC1000, label = "EPM155, top ~1000m", color='green', linestyle='dashed')
plt.scatter(dates155, DS155.HC2000, marker='.',  label = "EPM155, top ~2000m", s=0.5)#, color='red', linestyle='dashed')

plt.legend(loc='center left', bbox_to_anchor=(1,0.5))
#plt.xticks(rotation=45)
plt.title('Heat content in the LS convection region')
plt.ylabel('Heat content ($TJ$)')
plt.xlabel('Time')
plt.savefig('temp-EPM151vs155_HC_convectiveRegion.png', dpi=1200, bbox_inches="tight")
plt.close()

quit()

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.gca().xaxis.set_major_locator(mdates.YearLocator(base=1))

plt.plot(dates151, DS151.avgT50, label = "EPM151, top ~50m", color='blue')
plt.plot(dates151, DS151.avgT200, label = "EPM151, top ~200m", color='orange')
plt.plot(dates151, DS151.avgT1000, label = "EPM151, top ~1000m", color='green')
plt.plot(dates151, DS151.avgT2000, label = "EPM151, top ~2000m", color='red')
plt.plot(dates155, DS155.avgT50, label = "EPM155, top ~50m", color='blue', linestyle='dashed')
plt.plot(dates155, DS155.avgT200, label = "EPM155, top ~200m", color='orange', linestyle='dashed')
plt.plot(dates155, DS155.avgT1000, label = "EPM155, top ~1000m", color='green', linestyle='dashed')
plt.plot(dates155, DS155.avgT2000, label = "EPm155, top ~2000m", color='red', linestyle='dashed')

plt.legend(loc='center left', bbox_to_anchor=(1,0.5))
#plt.xticks(rotation=45)
plt.title('Average surface temperature in the LS convection region')
plt.ylabel('Temperature ($\degree C$)')
plt.xlabel('Time')
plt.savefig('temp-EPM151vs155_Temperature_convectiveRegion.png', dpi=1200, bbox_inches="tight")
plt.close()
