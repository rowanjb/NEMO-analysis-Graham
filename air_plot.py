#simple throwaway script making plots of data 

import matplotlib.pyplot as plt
import datetime
import matplotlib.dates as mdates
import xarray as xr
import LSmap 
import numpy as np 

def air_plot(mask, time_slice=False):

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))#'%m/%d/%Y'))
    interval = 2
    if time_slice: interval = 1
    plt.gca().xaxis.set_major_locator(mdates.YearLocator(interval))#(interval=365)) #with YearLocator(1) the ticks are at the start of the year

    #plt.style.use('tableau-colorblind10')
    #DSICE['heat_flux_timeplot'] = DSICE.heat_flux_in_each_cell.sum(dim=['x','y'])
    #DSICE.heat_flux_timeplot.to_netcdf(run + '_air/' + run + '_air_timeplot_' + mask_choice + '.nc')

    for run in ['EPM151','EPM152','EPM155','EPM156','EPM157','EPM158']:
        path = run + '_air/' + run + '_air_timeplot_' + mask + '.nc' 
        data2plot = xr.open_dataarray(path)
        #data2plot = data2plot.where(data2plot > 0, drop=True)
        if time_slice: data2plot = data2plot.sel(time_counter=slice('2010-01-01', '2014-01-01'))
        dates = data2plot.indexes['time_counter'].to_datetimeindex(unsafe=True) #Beware: warning turned off!!
        dates = [d.date() for d in dates]
        plt.plot(dates, data2plot, label = run, linewidth=0.5)
    
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.xticks(rotation=45)
    if mask == 'LS2k': mask_description = 'interior'
    elif mask == 'LS': mask_description = ''
    elif mask == 'LSCR': mask_description = 'convection region'
    titl = 'Total air-sea heat in flux the Labrador Sea ' + mask_description
    plt.title(titl)
    plt.ylabel('Heat flux ($W$, probably)') 
    plt.xlabel('Time')
    name = 'pics_air/air_timeplot_' + mask + '_over_time.png'
    if time_slice: name = 'pics_air/air_timeplot_' + mask + '_over_time_2010-2014.png' 
    plt.savefig(name, dpi=900, bbox_inches="tight")
    plt.clf()


if __name__ == "__main__":
    for i in ['LS2k','LSCR','LS']:
        air_plot(mask=i,time_slice=True)
        air_plot(mask=i,time_slice=False)

    #for mask in ['LSCR','LS2k','LS']:
    #    for time_slice in [True, False]:
    #        MLE_plot(mask, time_slice)

