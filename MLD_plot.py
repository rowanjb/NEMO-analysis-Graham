#simple throwaway script making plots of data 

import matplotlib.pyplot as plt
import datetime
import matplotlib.dates as mdates
import xarray as xr
import LSmap 
import numpy as np 

variable = 'avg_MLD' #max_MLD or avg_MLD
mask = 'LS2k' #LS2k or LS or LSCR
time_slice = True #whether you want a shorter slice of time

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))#'%m/%d/%Y'))
interval = 2
if time_slice: interval = 1
plt.gca().xaxis.set_major_locator(mdates.YearLocator(interval))#(interval=365)) #with YearLocator(1) the ticks are at the start of the year

for run in ['EPM151','EPM152','EPM155','EPM156','EPM157','EPM158']:
    path = run + '_MLD/' + run + '_' + variable + '_time_plot_' + mask + '.nc'
    data2plot = xr.open_dataarray(path)
    #if variable=='max_MLD': 
    #    data2plot = data2plot.where(data2plot <= -1000)#, drop=True)
    #    data2plot = -1*data2plot

    if time_slice: data2plot = data2plot.sel(time_counter=slice('2010-01-01', '2014-01-01'))
    dates = data2plot.indexes['time_counter'].to_datetimeindex(unsafe=True) #Beware: warning turned off!!
    dates = [d.date() for d in dates]
    plt.plot(dates, data2plot, label = run, linewidth=0.5)

plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.xticks(rotation=45)
if mask == 'LS2k': mask_description = 'interior'
elif mask == 'LS': mask_description = ''
elif mask == 'LSCR': mask_description = 'convection region'
if variable=='max_MLD': titl = 'Max mixed layer depth in \nthe Labrador Sea ' + mask_description
if variable=='avg_MLD': titl = 'Average mixed layer depth in \nthe Labrador Sea ' + mask_description
plt.title(titl)
plt.ylabel('MLD ($m$)')
plt.xlabel('Time')
name = 'pics_MLD/' + variable + '_' + mask + '_over_time.png'
if time_slice: name = 'pics_MLD/' + variable + '_' + mask + '_over_time_2010-2014.png' 
plt.savefig(name, dpi=900, bbox_inches="tight")
plt.clf()

#maxMLD_col.to_netcdf(run + '_MLD/' + run + '_max_MLD_map_' + mask_choice + '.nc')
#maxMLD_region.to_netcdf(run + '_MLD/' + run + '_max_MLD_time_plot_' + mask_choice + '.nc')
#avgMLD_col.to_netcdf(run + '_MLD/' + run + '_avg_MLD_map_' + mask_choice + '.nc')
#avgMLD_region.to_netcdf(run + '_MLD/' + run + '_avg_MLD_time_plot_' + mask_choice + '.nc')
