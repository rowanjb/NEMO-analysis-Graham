#simple throwaway script making maps of data 

import xarray as xr
import LSmap 
import numpy as np 
import math

difference_plot = False #if false, just plots the first run
variable = 'votemper'
mask = 'LS' #LS or LSCR or LS2k, though if you plot LS it captures LSCR and LS2k anyway...
run1 = 'EPM158'
run2 = 'EPM155'

for depth in ['50','200','1000','2000']:

    path1 = run1 + '_heat/' + run1 + '_' + variable + '_timeAvg_' + mask + depth + '.nc'
    da1 = xr.open_dataarray(path1)

    path2 = run2 + '_heat/' + run2 + '_' + variable + '_timeAvg_' + mask + depth + '.nc'
    da2 = xr.open_dataarray(path2)

    #dealing within masked areas where HC=0
    if variable=='HC':
        da1 = da1.where(da1 > 0)
        da2 = da2.where(da2 > 0)

    if difference_plot: 
        da = da1-da2
    else:
        da = da1 

    minmax = LSmap.xrLSminmax(da,da.nav_lat_grid_T,da.nav_lon_grid_T)
    #mn = math.floor(minmax[0])
    #mx = math.ceil(minmax[1])
    #minmax = mn,mx
    
    if difference_plot:
        if variable=='votemper': CBlabel = '$\Delta$T ($\degree C$)'
        if variable=='HC': CBlabel = '$\Delta$HC ($J$)'
    else:
        if variable=='votemper': CBlabel = 'T ($\degree C$)'
        if variable=='HC': CBlabel = 'HC ($J$)'

    if mask == 'LS2k': mask_description = ' interior'
    elif mask == 'LS': mask_description = ''
    elif mask == 'LSCR': mask_description = ' convection region'
    
    if difference_plot:
        if variable=='votemper': title = 'Difference in average temperature in the top ' + depth + 'm of \nthe Labrador Sea' + mask_description + ', ' + run1 + '-' + run2
        if variable=='HC': title = 'Difference in heat content in the top ' + depth + 'm of \nthe Labrador Sea' + mask_description + ', ' + run1 + '-' + run2
    else:
        if variable=='votemper': title = 'Average temperature in the top ' + depth + 'm of \nthe Labrador Sea' + mask_description + ', ' + run1
        if variable=='HC': title = 'Heat content in the top ' + depth + 'm of \nthe Labrador Sea' + mask_description + ', ' + run1

    if difference_plot:
        fileName  = 'pics_heat/' + run1 + '-' + run2 + '_' + variable + '_map_' + mask + depth
    else:
        fileName = 'pics_heat/' + run1 + '_' + variable + '_map_' + mask + depth
    
    LSmap.LSmap(da,da.nav_lon_grid_T,da.nav_lat_grid_T,minmax,CBlabel,title,fileName)

quit()

##simple throwaway script making maps of data 
#  
#import matplotlib.pyplot as plt
#import datetime
#import matplotlib.dates as mdates
#import xarray as xr
#import LSmap
#import numpy as np
#
#variable = 'votemper' #HC or votemper
#mask = 'LS2k' #LS2k or LS or LSCR
#depth = '2000' #50 or 200 or 1000 or 2000
#time_slice = False #whether you want a shorter slice of time
#
#plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))#'%m/%d/%Y'))
#plt.gca().xaxis.set_major_locator(mdates.YearLocator(2))#(interval=365)) #with YearLocator(1) the ticks are at the start of the year
#
#for run in ['EPM151','EPM152','EPM155','EPM156','EPM157','EPM158']:
#    if variable=='votemper': path_variable = '_votemper_spaceAvg_'
#    if variable=='HC': path_variable = '_HC_spaceSum_'
#    path = run + '_heat/' + run + path_variable + mask + depth + '.nc'
#    data2plot = xr.open_dataarray(path)
#    if variable=='HC': data2plot = data2plot.where(data2plot > 1000)#, drop=True)
#    if time_slice: data2plot = data2plot.sel(time_counter=slice('2010-01-01', '2014-01-01'))
#    dates = data2plot.indexes['time_counter'].to_datetimeindex(unsafe=True) #Beware: warning turned off!!
#    dates = [d.date() for d in dates]
#    plt.plot(dates, data2plot, label = run, linewidth=0.5)
#
#plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
#plt.xticks(rotation=45)
#if mask == 'LS2k': mask_description = 'interior'
#elif mask == 'LS': mask_description = ''
#elif mask == 'LSCR': mask_description = 'convection region'
#if variable=='votemper': titl = 'Temperature in the top ' + depth + 'm of \nthe Labrador Sea ' + mask_description
#if variable=='HC': titl = 'Heat content in the top ' + depth + 'm of \nthe Labrador Sea ' + mask_description
#plt.title(titl)
#plt.ylabel('HC ($J$)')
#plt.xlabel('Time')
#name = 'pics_heat/' + variable + '_' + mask + depth + '_over_time.png'
#if time_slice: name = 'pics_heat/' + variable + '_' + mask + depth + '_over_time_2010-2014.png'
#plt.savefig(name, dpi=900, bbox_inches="tight")
#~                                                   
