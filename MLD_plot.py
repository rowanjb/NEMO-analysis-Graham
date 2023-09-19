#simple throwaway script making plots of data 

import matplotlib.pyplot as plt
import datetime
import matplotlib.dates as mdates
import xarray as xr
import LSmap 
import numpy as np 

def MLD_plot(variable, mask, time_slice):

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
    name = 'pics_MLD/' + variable + '_' + mask + '_over_time'
    if time_slice: name = name + '_2010-2014'
    name = name + '.png'
    plt.savefig(name, dpi=900, bbox_inches="tight")
    plt.clf()

def MLD_plot_with_Argo(variable, mask):

    #plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m'))#'%m/%d/%Y'))
    #plt.gca().xaxis.set_major_locator(mdates.MonthLocator)#(interval=365)) #with YearLocator(1) the ticks are at the start of the year

    for run in ['EPM151']:#,'EPM152','EPM155','EPM156','EPM157','EPM158']:
        path = run + '_MLD/' + run + '_' + variable + '_time_plot_' + mask + '.nc'
        data2plot = xr.open_dataarray(path)
        monthly_data2plot = data2plot.groupby("time_counter.month").mean("time_counter")
        #dates = data2plot.indexes['time_counter'].to_datetimeindex(unsafe=True) #Beware: warning turned off!!
        #dates = [d.date() for d in dates]
        plt.plot(monthly_data2plot.month, monthly_data2plot, label = run, linewidth=0.5)

    if mask == 'LS2k':
        with xr.open_dataarray('masks/mask_LS_2k.nc') as DS:
            DAmask = DS.astype(int).rename({'deptht':'z','x_grid_T':'x','y_grid_T':'y'})
    elif mask == 'LS':
        with xr.open_dataarray('masks/mask_LS.nc') as DS:
            DAmask = DS.astype(int).rename({'deptht':'z','x_grid_T':'x','y_grid_T':'y'})
    elif mask == 'LSCR':
        with xr.open_dataset('masks/ARGOProfiles_mask.nc') as DS:
            DAmask = DS.astype(int)
    else:
        print("Y'all didn't choose a mask")
        quit()

    print(DAmask)


    Argo = xr.open_dataset('Argo_mixedlayers_monthlyclim_04142022.nc')
    #MASK
    plt.plot(Argo.month, Argo.mld_da_mean.mean(dim=['iLAT','iLON']), label = 'Argo')
    #dates = Argo.indexes['iMONTH'].to_datetimeindex(unsafe=True)
    #print(dates)

    #ADD IN FUNCTIONALITY FOR MASKING OBSERVATIONAL DATA

    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.xticks(rotation=45)
    if mask == 'LS2k': mask_description = 'interior'
    elif mask == 'LS': mask_description = ''
    elif mask == 'LSCR': mask_description = 'convection region'
    if variable=='max_MLD': titl = 'Max mixed layer depth in \nthe Labrador Sea ' + mask_description
    if variable=='avg_MLD': titl = 'Average mixed layer depth in \nthe Labrador Sea ' + mask_description
    plt.title(titl)
    plt.ylabel('MLD ($m$)')
    plt.xlabel('Month')
    name = 'pics_MLD/' + variable + '_' + mask + '_over_time'
    name = name + 'tesssssssssssssssssssst.png'
    plt.savefig(name, dpi=900, bbox_inches="tight")
    plt.clf()


if __name__ == "__main__":
    variable = 'avg_MLD' #max_MLD or avg_MLD
    mask = 'LSCR' #LS2k or LS or LSCR
    time_slice = False #whether you want a shorter slice of time
    #MLD_plot(variable, mask, time_slice)
    MLD_plot_with_Argo(variable, mask)
