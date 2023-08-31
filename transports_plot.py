#simple throwaway script making plots of data 
  
import matplotlib.pyplot as plt
import datetime
import matplotlib.dates as mdates
import xarray as xr
import LSmap
import numpy as np

section = 'ANHA4_LS2000mIsobath'
variable = 'volume'
time_slice = False #whether you want a shorter slice of time

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))#'%m/%d/%Y'))
interval = 2
if time_slice: interval = 1
plt.gca().xaxis.set_major_locator(mdates.YearLocator(interval))#(interval=365)) #with YearLocator(1) the ticks are at the start of the year

for run in ['EPM151','EPM152','EPM155','EPM156','EPM157','EPM158']:
    path = 'pics_transports/' + section + '_' + variable + '_transport_' + run + '.nc'
    data2plot = xr.open_dataarray(path)
    if time_slice: data2plot = data2plot.sel(time_counter=slice('2010-01-01', '2014-01-01'))
    dates = data2plot.indexes['time_counter'].to_datetimeindex(unsafe=True) #Beware: warning turned off!!
    dates = [d.date() for d in dates]
    plt.plot(dates, data2plot, label = run, linewidth=0.5)

plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.xticks(rotation=45)
if section == 'ANHA4_LS2000mIsobath': section_title = 'Labrador Sea 2000 m isobath'
elif section == 'OSNAP': section_title = 'OSNAP West section'
elif section == 'AR7W': section_title = 'AR7W section'
titl = variable.capitalize() + " transport through the " + section_title
plt.title(titl)
if variable == 'volume': y_label = 'Volume flux ($Sv$)' #($m^3$ $s^{-1}$)    MIGHT BE SV??'
elif variable == 'freshwater': y_label = 'Freshwater flux ($Sv$)' #($m^3$ $s^{-1}$)  MIGHT BE SV?'
elif variable == 'heat': y_label = 'Heat flux ($J$ $s^{-1}$)... probably'
elif variable == 'salt': y_label = 'Salt flux ($kg$ $s^{-1}$)... maybe'
plt.ylabel(y_label)
plt.xlabel('Time')
name = 'pics_transports/' + section + '_' + variable + '_over_time.png'
if time_slice: name = 'pics_transports/' + section + '_' + variable + '_over_time_2010-2014.png'
plt.savefig(name, dpi=900, bbox_inches="tight")
plt.clf()
