#simple throwaway script making maps of data 

import xarray as xr
import LSmap 
import numpy as np 
import math
import os

def mld_map(variable, mask, run1, run2=False):
    
    path1 = run1 + '_MLD/' + run1 + '_' + variable + '_map_' + mask + '.nc'
    da1 = xr.open_dataarray(path1)

    if run2!=False:
        path2 = run2 + '_MLD/' + run2 + '_' + variable + '_map_' + mask + '.nc'
        da2 = xr.open_dataarray(path2)
        da = da1-da2    
    else:
        da = da1

    minmax = LSmap.xrLSminmax(da,da.nav_lat_grid_T,da.nav_lon_grid_T)

    CBlabel = 'MLD depth ($m$)'

    if run2!=False:
        if variable=='max_MLD': title = 'Difference of the max mixed layer depth in \nthe Labrador Sea, ' + run1 + '-' + run2
        if variable=='avg_MLD': title = 'Difference of the average mixed layer depth in \nthe Labrador Sea, ' + run1 + '-' + run2
        fileName  = 'pics_MLD/' + run1 + '-' + run2 + '_' + variable + '_map_' + mask
    else:
        if variable=='max_MLD': title = 'Max mixed layer depth in the Labrador Sea, ' + run1 
        if variable=='avg_MLD': title = 'Average mixed layer depth in the Labrador Sea, ' + run1 
        fileName  = 'pics_MLD/' + run1 + '_' + variable + '_map_' + mask
    
    LSmap.LSmap(da,da.nav_lon_grid_T,da.nav_lat_grid_T,minmax,CBlabel,title,fileName)#,scale='log')

def mld_movie_frames(mask, run1):
    folder = run1 + '_MLD/movie_NCs/'
    movie_files = sorted([folder + file for file in os.listdir(folder)])
    for i in movie_files:
        date = i[-13:-3]
        da = xr.open_dataarray(i)
        #minmax = LSmap.xrLSminmax(da,da.nav_lat_grid_T,da.nav_lon_grid_T)
        CBlabel = 'MLD ($m$)'
        title = 'Mixed layer depth in the Labrador Sea\n' + run1 + ' - ' + date
        folder = run1 + '_MLD/movie_frames' 
        if not os.path.exists(folder):
            os.makedirs(folder)
        filename = folder + '/' + run1 + '_MLD_map_' + date
        LSmap.LSmap(da,da.nav_lon_grid_T,da.nav_lat_grid_T,(0,2500),CBlabel,title,filename)

if __name__ == "__main__":
    #mld_map(variable='avg_MLD', mask='LS', run1='EPM158')
    #mld_map(variable='max_MLD', mask='LS', run1='EPM158')
    for i in ['EPM151','EPM152','EPM155','EPM156','EPM157','EPM158']:
        mld_movie_frames(mask='LS', run1=i)

#def mle_movie_frames(mask, run1):
#    folder = run1 + '_MLE/movie_NCs/'
#    movie_files = sorted([folder + file for file in os.listdir(folder)])
#    for i in movie_files:
#        date = i[-13:-3]
#        da = xr.open_dataarray(i)
#        #minmax = LSmap.xrLSminmax(da,da.nav_lat_grid_T,da.nav_lon_grid_T)
#        CBlabel = 'Heat flux ($J/S$?)'
#        title = 'Average heat flux through the bottom of the mixed layer, \n' + run1 + ' - ' + date
#        fileName  = run1 + '_MLE/movie_frames/' + run1 + '_MLE_Q_map_' + date
#        LSmap.LSmap(da,da.nav_lon_grid_T,da.nav_lat_grid_T,(0,5000),CBlabel,title,fileName)#,scale='log')

