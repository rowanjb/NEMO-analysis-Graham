#simple throwaway script making plots of data 

import matplotlib.pyplot as plt
import datetime
import matplotlib.dates as mdates
import xarray as xr
import LSmap
import numpy as np

def profilePlot(variable,section,run1,run2=False):

    path = run1 + '_crossSection/' + run1 + '_' + section + '_' + variable + '.nc'
    da1 = xr.open_dataarray(path)
    da1 = da1.where(da1 != 0) #i.e., land

    if run2!=False:
        path = run2 + '_crossSection/' + run2 + '_' + section + '_' + variable + '.nc'
        da2 = xr.open_dataarray(path)
        da2 = da2.where(da2 != 0) #i.e., land
        da = da1 - da2
        pathName = 'pics_crossSection/' + run1 + '-' + run2 + '_' + section + '_' + variable + '.png'
    else:
        da = da1
        pathName = 'pics_crossSection/' + run1 + '_' + section + '_' + variable + '.png'

    if run2==False:
        if variable == 'vel': 
            cbLabel = 'Velocity ($m$ $s^{-2}$)'
            if section == 'OSNAP': title = 'Cross sectional velocity profile, OSNAP West, ' + run1
            else: title = 'Cross sectional velocity profile, ' + section + ', ' + run1
        elif variable == 'vosaline': 
            cbLabel = 'Salinity ($PSU$)'
            if section == 'OSNAP': title = 'Salinity profile, OSNAP West, ' + run1
            else: title = 'Salinity profile, ' + section + ', ' + run1
        elif variable == 'votemper': 
            cbLabel = 'Temperature ($\degree C$)'
            if section == 'OSNAP': title = 'Temperature profile, OSNAP West, ' + run1
            else: title = 'Temperature profile, ' + section + ', ' + run1
    else:
        if variable == 'vel':
            cbLabel = '$\Delta$Velocity ($m$ $s^{-2}$)'
            if section == 'OSNAP': title = 'Difference in cross sectional \nvelocity, OSNAP West, ' + run1 + '-' + run2
            else: title = 'Difference in cross sectional velocity, \n' + section + ', ' + run1 + '-' + run2
        elif variable == 'vosaline':
            cbLabel = '$\Delta$Salinity ($PSU$)'
            if section == 'OSNAP': title = 'Difference in salinity, OSNAP West, ' + run1 + '-' + run2
            else: title = 'Difference in salinity, ' + section + ', ' + run1 + '-' + run2
        elif variable == 'votemper':
            cbLabel = '$\Delta$Temperature ($\degree C$)'
            if section == 'OSNAP': title = 'Difference in temperature, OSNAP West, ' + run1 + '-' + run2
            else: title = 'Difference in temperature, ' + section + ', ' + run1 + '-' + run2

    da['dists'] = da.dists/1000 #convert to km

    da.plot.contourf(
            x='dists',
            y='z',
            ylim=[4000,0],
            center=False,
            add_labels=True,
            levels=10,
            cmap="viridis",
            cbar_kwargs={'label': cbLabel}
    )

    plt.title(title)
    plt.xlabel('Distance along section ($km$)')
    plt.ylabel('Depth ($m$)')
    plt.savefig(pathName, dpi=900, bbox_inches="tight")
    plt.clf()

    return

if __name__ == "__main__":
    for variable in ['votemper','vel','vosaline']:    
        for section in ['OSNAP','AR7W']:
            profilePlot(variable,section,run1='EPM151',run2='EPM155')
    for variable in ['votemper','vel','vosaline']:
        for section in ['OSNAP','AR7W']:
            profilePlot(variable,section,run1='EPM151',run2='EPM157')
    for variable in ['votemper','vel','vosaline']:
        for section in ['OSNAP','AR7W']:
            profilePlot(variable,section,run1='EPM155',run2='EPM157')
    for variable in ['votemper','vel','vosaline']:
        for section in ['OSNAP','AR7W']:
            profilePlot(variable,section,run1='EPM152',run2='EPM156')
    for variable in ['votemper','vel','vosaline']:
        for section in ['OSNAP','AR7W']:
            profilePlot(variable,section,run1='EPM152',run2='EPM158')
    for variable in ['votemper','vel','vosaline']:
        for section in ['OSNAP','AR7W']:
            profilePlot(variable,section,run1='EPM156',run2='EPM158')
    for variable in ['votemper','vel','vosaline']:
        for section in ['OSNAP','AR7W']:
            for run in ['EPM151','EPM152','EPM155','EPM156','EPM157','EPM158']:
                profilePlot(variable,section,run1=run)


