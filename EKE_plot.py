#simple throwaway script making plots of data 
  
import matplotlib.pyplot as plt
import datetime
import matplotlib.dates as mdates
import xarray as xr
import LSmap
import numpy as np

def EKE_plot(mask, time_slice):

    for depth in ['50','200','1000','2000']:

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))#'%m/%d/%Y'))
        interval = 2
        if time_slice: interval = 1
        plt.gca().xaxis.set_major_locator(mdates.YearLocator(interval))#(interval=365)) #with YearLocator(1) the ticks are at the start of the year

        for run in ['EPM151','EPM152','EPM155','EPM156','EPM157','EPM158']:
            
            path = run + '_EKE/' + run + '_EKE_timePlot_' + mask + depth + '.nc'
            data2plot = xr.open_dataarray(path)
            data2plot = data2plot.where(data2plot > 10, drop=True)
        
            data2plot = data2plot.rolling(time_counter=19,center=True).mean().dropna("time_counter")

            if time_slice: data2plot = data2plot.sel(time_counter=slice('2010-01-01', '2014-01-01'))
            dates = data2plot.indexes['time_counter'].to_datetimeindex(unsafe=True) #Beware: warning turned off!!
            dates = [d.date() for d in dates]
            plt.plot(dates, data2plot, label = run, linewidth=0.5)

        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.xticks(rotation=45)
        if mask == 'LS2k': mask_description = 'interior'
        elif mask == 'LS': mask_description = ''
        elif mask == 'LSCR': mask_description = 'convection region'
        titl = 'Total eddy kinetic energy in the top ' + depth + 'm of \nthe Labrador Sea ' + mask_description
        plt.title(titl)
        plt.ylabel('EKE ($J$)')
        plt.xlabel('Time')
        name = 'pics_EKE/' + 'EKE_' + mask + depth + '_over_time.png'
        if time_slice: name = 'pics_EKE/' + 'EKE_' + mask + depth + '_over_time_2010-2014.png'
        plt.savefig(name, dpi=900, bbox_inches="tight")
        plt.clf()

if __name__ == "__main__":
    EKE_plot(mask='LSCR', time_slice=True)    
    EKE_plot(mask='LSCR', time_slice=False)
    EKE_plot(mask='LS2k', time_slice=True)                        
    EKE_plot(mask='LS2k', time_slice=False)
    EKE_plot(mask='LS', time_slice=True)                        
    EKE_plot(mask='LS', time_slice=False)


##simple throwaway script making maps of data 
#
#import matplotlib.pyplot as plt
#import datetime
#import matplotlib.dates as mdates
#import xarray as xr
#import LSmap 
#import numpy as np 
#
#path = 'EPM151_EKE/EPM151_EKE_timePlot_LS2000.nc'
#EKE = xr.open_dataarray(path)
#
##minmax = LSmap.xrLSminmax(EKE,EKE.nav_lat_grid_T,EKE.nav_lon_grid_T)
##CBlabel = 'EKE ($J$)'
##title = 'Test map of EKE in LS'
##fileName  = 'test_map_EKE'
##LSmap.LSmap(EKE,EKE.nav_lon_grid_T,EKE.nav_lat_grid_T,minmax,CBlabel,title,fileName,scale='log')
#
#dates = EKE.indexes['time_counter'].to_datetimeindex(unsafe=True) #Beware: warning turned off!!
#dates = [d.date() for d in dates]
#plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
#plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=800))
#plt.plot(dates, EKE, label = "test label")
##plt.plot(dates, DS.HC50, label = "Top ~50m")
##plt.plot(dates, DS.HC200, label = "Top ~200m")
##plt.plot(dates, DS.HC1000, label = "Top ~1000m")
##plt.plot(dates, DS.HC2000, label = "Top ~2000m")
#plt.legend()
#plt.xticks(rotation=45)
#plt.title('EKE, or something...')
#plt.ylabel('EKE (J)')
#plt.xlabel('Time')
#plt.savefig('deletable-test-image.png', dpi=900, bbox_inches="tight")
#plt.close()
##
