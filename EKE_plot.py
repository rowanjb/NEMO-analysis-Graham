#simple throwaway script making maps of data 

import matplotlib.pyplot as plt
import datetime
import matplotlib.dates as mdates
import xarray as xr
import LSmap 
import numpy as np 

path = 'EPM151_EKE/EPM151_EKE_regionAvg_LS50.nc'
EKE = xr.open_dataarray(path)

#minmax = LSmap.xrLSminmax(EKE,EKE.nav_lat_grid_T,EKE.nav_lon_grid_T)
#CBlabel = 'EKE ($J$)'
#title = 'Test map of EKE in LS'
#fileName  = 'test_map_EKE'
#LSmap.LSmap(EKE,EKE.nav_lon_grid_T,EKE.nav_lat_grid_T,minmax,CBlabel,title,fileName,scale='log')

dates = EKE.indexes['time_counter'].to_datetimeindex(unsafe=True) #Beware: warning turned off!!
dates = [d.date() for d in dates]
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=800))
plt.plot(dates, EKE, label = "test label")
#plt.plot(dates, DS.HC50, label = "Top ~50m")
#plt.plot(dates, DS.HC200, label = "Top ~200m")
#plt.plot(dates, DS.HC1000, label = "Top ~1000m")
#plt.plot(dates, DS.HC2000, label = "Top ~2000m")
plt.legend()
plt.xticks(rotation=45)
plt.title('EKE, or something...')
plt.ylabel('EKE (J)')
plt.xlabel('Time')
plt.savefig('deletable-test-image.png', dpi=900, bbox_inches="tight")
plt.close()

