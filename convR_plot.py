#simple throwaway script making plots of data 

import matplotlib.pyplot as plt
import datetime
import matplotlib.dates as mdates
import xarray as xr
import LSmap 
import numpy as np 

mask = 'LSCR' #LS2k or LS or LSCR
depth = '2000' #50 or 200 or 1000 or 2000
time_slice = False #whether you want a shorter slice of time

for depth in ['50','200','1000','2000']:

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))#'%m/%d/%Y'))
    interval = 2
    if time_slice: interval = 1
    plt.gca().xaxis.set_major_locator(mdates.YearLocator(interval))#(interval=365)) #with YearLocator(1) the ticks are at the start of the year

    for run in ['EPM158']:#['EPM151','EPM152','EPM155','EPM156','EPM157','EPM158']:
        path = run + '_convR/' + run + '_convR_plot_' + mask + depth + '.nc' #EPM158_convR_plot_LSCR1000.nc
        data2plot = xr.open_dataarray(path)
        if time_slice: data2plot = data2plot.sel(time_counter=slice('2010-01-01', '2014-01-01'))
        dates = data2plot.indexes['time_counter'].to_datetimeindex(unsafe=True) #Beware: warning turned off!!
        dates = [d.date() for d in dates]
        plt.plot(dates, data2plot, label = run, linewidth=0.5)

    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.xticks(rotation=45)
    if mask == 'LS2k': mask_description = 'interior'
    elif mask == 'LS': mask_description = ''
    elif mask == 'LSCR': mask_description = 'convection region'
    titl = 'Convective resistance in the top ' + depth + 'm of \nthe Labrador Sea ' + mask_description
    plt.title(titl)
    plt.ylabel('Convective resistance ($J/m^3$)') 
    plt.xlabel('Time')
    name = 'pics_convR/convR_plot_' + mask + depth + '_over_time.png'
    if time_slice: name = 'pics_convR/convR_plot_' + mask + depth + '_over_time_2010-2014.png' 
    plt.savefig(name, dpi=900, bbox_inches="tight")
    plt.clf()

quit()
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
