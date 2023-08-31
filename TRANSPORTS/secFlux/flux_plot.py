#simple throwaway script making plots of data 

import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates
import xarray as xr
import numpy as np
import scipy.io as spio

def fluxPlot(section,window_size=1,rolling_window=False,time_slice=False):

    for variable in ['myVol','myHeat','mySalt','myFW']:

        for run in ['EPM151','EPM152','EPM155','EPM156','EPM157','EPM158']:
            
            if run=='EPM151': date_range = '2002_2021' 
            elif run=='EPM152': date_range = '2002_2019'
            elif run=='EPM155': date_range = '2002_2021' 
            elif run=='EPM156': date_range = '2002_2019'
            elif run=='EPM157': date_range = '2002_2021'
            elif run=='EPM158': date_range = '2002_2018'

            path = 'ANHA4-' + run + '/' + section + '_ANHA4-' + run + '_' + date_range + '.mat'
            mat = spio.loadmat(path)
            timeTag = mat['timeTag']
            timeTag = [datetime.strptime(date[0][0],'y%Ym%md%d') for date in timeTag]
            data2plot = mat[variable]
            data2plot = [i[0] for i in data2plot]

            if rolling_window:
                data2plot = [np.nan if i==0 else i for i in data2plot]
                avg_period = window_size #ie 2 outputs on either side, so 5 total (25 days)
                timeTag = timeTag[avg_period:-avg_period]
                avg_data2plot = []
                for n,i in enumerate(data2plot[ avg_period : -avg_period ]):
                    n = n + avg_period
                    avged_data = np.nanmean(data2plot[n-avg_period:n+avg_period]) #/(1+2*avg_period))
                    avg_data2plot = np.append(avg_data2plot,avged_data)
                data2plot = avg_data2plot

            plt.plot(timeTag, data2plot, label = run, linewidth=0.5)

        if variable=='myVol': 
            if section=='ANHA4_LabSea2kDepth': title = 'Volume flux into the interior Labrador Sea\nacross the 2000 m isobath'
            elif section =='ANHA4_WGC2kDepth': title = 'Volume flux from the West Greenland Current\ninto the interior Labrador Sea across the 2000 m isobath'
            elif section =='ANHA4_LC2kDepth': title = 'Volume flux from the Labrador Current into\nthe interior Labrador Sea across the 2000 m isobath'
            elif section =='ANHA4_LSsouth': title = 'Volume flux from the interior Labrador Sea into the North Atlantic'
            y_axis_label = 'Volume flux ($m^3$ $s^{-1}$)'
        if variable=='myHeat':
            if section=='ANHA4_LabSea2kDepth': title = 'Heat flux into the interior Labrador Sea\nacross the 2000 m isobath'
            elif section =='ANHA4_WGC2kDepth': title = 'Heat flux from the West Greenland Current\ninto the interior Labrador Sea across the 2000 m isobath'
            elif section =='ANHA4_LC2kDepth': title = 'Heat flux from the Labrador Current into\nthe interior Labrador Sea across the 2000 m isobath'
            elif section =='ANHA4_LSsouth': title = 'Heat flux from the interior Labrador Sea into the North Atlantic'
            y_axis_label = 'Heat flux ($TW$)'
        if variable=='mySalt':
            if section=='ANHA4_LabSea2kDepth': title = 'Salt flux into the interior Labrador Sea\nacross the 2000 m isobath'
            elif section =='ANHA4_WGC2kDepth': title = 'Salt flux from the West Greenland Current\ninto the interior Labrador Sea across the 2000 m isobath'
            elif section =='ANHA4_LC2kDepth': title = 'Salt flux from the Labrador Current into\nthe interior Labrador Sea across the 2000 m isobath'
            elif section =='ANHA4_LSsouth': title = 'Salt flux from the interior Labrador Sea into the North Atlantic'
            y_axis_label = 'Salt flux ($kt$ $s^{-1}$)'
        if variable=='myFW':
            if section=='ANHA4_LabSea2kDepth': title = 'Fresh water flux into the interior Labrador Sea\nacross the 2000 m isobath'
            elif section =='ANHA4_WGC2kDepth': title = 'Fresh water flux from the West Greenland Current\ninto the interior Labrador Sea across the 2000 m isobath'
            elif section =='ANHA4_LC2kDepth': title = 'Fresh water flux from the Labrador Current into\nthe interior Labrador Sea across the 2000 m isobath'
            elif section =='ANHA4_LSsouth': title = 'Fresh water flux from the interior Labrador Sea into the North Atlantic'
            y_axis_label = 'Fresh water flux ($m^3$ $s^{-1}$)'

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        interval = 2 
        if time_slice:
            interval = 1
            plt.xlim( datetime(2010, 1, 1, 0, 0) , datetime(2014, 1, 1, 0, 0))
        plt.gca().xaxis.set_major_locator(mdates.YearLocator(interval))
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.xticks(rotation=45)
        plt.title(title)
        plt.ylabel(y_axis_label)
        plt.xlabel('Time')
        folderPath = '/home/rowan/projects/rrg-pmyers-ad/rowan/NEMO-analysis-Graham/pics_fluxes/'
        name = folderPath + section + '_' + variable
        if rolling_window: name = name + '_' + 'rollingWindow' + str(avg_period)
        if time_slice: name = name + '_' + 'time_slice'
        plt.savefig(name + '.png', dpi=900, bbox_inches="tight")
        plt.clf()

    return

if __name__ == "__main__":
    
    section = 'ANHA4_LSsouth' #ANHA4_WGC2kDepth_ANHA4-EPM155_2002_2021.mat ANHA4_LabSea2kDepth_ANHA4-EPM155_2002_2021.mat ANHA4_LC2kDepth_ANHA4-EPM156_2002_2019.mat 
    fluxPlot(section,time_slice=True)
    fluxPlot(section)
    fluxPlot(section,window_size=9,rolling_window=True,time_slice=True)
    fluxPlot(section,window_size=5,rolling_window=True,time_slice=True)
    fluxPlot(section,window_size=2,rolling_window=True,time_slice=True)
    fluxPlot(section,window_size=9,rolling_window=True)
    fluxPlot(section,window_size=5,rolling_window=True)
    fluxPlot(section,window_size=2,rolling_window=True)

