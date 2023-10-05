#simple throwaway script making maps of data 

import xarray as xr
import LSmap 
import numpy as np 
import math

def air_map(mask, run1, run2=False):
    
    #DSICE['heat_flux_map'] = DSICE.heat_flux_in_each_cell.mean(dim='time_counter')
    #DSICE.heat_flux_map.to_netcdf(run + '_air/' + run + '_air_map_' + mask_choice + '.nc')

    path1 = run1 + '_air/' + run1 + '_air_map_' + mask + '.nc'
    da1 = xr.open_dataarray(path1)

    if run2!=False:
        path2 = run2 + '_air/' + run2 + '_air_map_' + mask + '.nc'
        da2 = xr.open_dataarray(path2)
        da = da1-da2    
    else:
        da = da1

    minmax = LSmap.xrLSminmax(da,da.nav_lat,da.nav_lon)

    CBlabel = 'Heat flux ($W$ $m^{-2}$)'

    if run2!=False:
        title = 'Difference in the air-sea heat fluxes in \nthe Labrador Sea, ' + run1 + '-' + run2
        fileName  = 'pics_air/' + run1 + '-' + run2 + '_ao_heatFlux_map_' + mask
    else:
        title = 'Average downward air-sea heat flux, ' + run1 
        fileName  = 'pics_air/' + run1 + '_air_map_' + mask
    
    LSmap.LSmap(da,da.nav_lon,da.nav_lat,minmax,CBlabel,title,fileName)#,scale='log') (0e10,-4e10)

if __name__ == "__main__":
    #for i in ['EPM151','EPM152','EPM155','EPM156','EPM157','EPM158']:
    #    for j in ['LS','LS2k','LSCR']:
    #        air_map(mask=j,run1=i)

    air_map(mask='LS',run1='EPM151',run2='EPM155')
    air_map(mask='LS',run1='EPM151',run2='EPM157')
    air_map(mask='LS',run1='EPM155',run2='EPM157')
    air_map(mask='LS',run1='EPM152',run2='EPM156')
    air_map(mask='LS',run1='EPM152',run2='EPM158')
    air_map(mask='LS',run1='EPM156',run2='EPM158')
    

    #for i in ['EPM151','EPM152','EPM155','EPM156','EPM157','EPM158']:
    #    mle_map(mask='LS', run1=i)
    #mld_map(variable='avg_MLD', mask='LS', run1='EPM158')
    #mld_map(variable='max_MLD', mask='LS', run1='EPM158')
