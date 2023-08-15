#simple throwaway script making maps of data 
#maps average current velocity in the surface

import xarray as xr
import LSmap 
import numpy as np 
import math

import matplotlib.pyplot as plt
import matplotlib.path as mpath
import cartopy.crs as ccrs
import cartopy.feature as feature
import matplotlib.ticker as mticker
import matplotlib.colors as colors

def mapCurrentVelocities(mask, run1, d):

    path1 = run1 + '_currentVel/' + run1 + '_avgCurrentVel_map_' + mask + str(d) + '.nc'
    ds = xr.open_dataset(path1)

    #getting the absolute velocities 
    vel = ((ds.U**2) + (ds.V**2))**0.5

    #getting the min vel and max vel for colourbar purposes
    minmax = LSmap.xrLSminmax(vel,vel.nav_lat_grid_T,vel.nav_lon_grid_T)

    #grid extents for map
    westLon = -70
    eastLon = -35
    northLat = 70
    southLat = 50

    #shapefile of land with 1:50,000,000 scale
    land_50m = feature.NaturalEarthFeature('physical', 'land', '50m',edgecolor='black', facecolor='gray')

    #defining the projection, note that standard parallels are the parallels of correct scale
    projection = ccrs.AlbersEqualArea(central_longitude=-55, central_latitude=50,standard_parallels=(southLat,northLat))

    #create figure (using the specified projection)
    ax = plt.subplot(1, 1, 1, projection=projection)

    #define map dimensions (using Plate Carree coordinate system)
    ax.set_extent([westLon, eastLon, southLat, northLat], crs=ccrs.PlateCarree())

    #add land to map
    ax.add_feature(land_50m, color=[0.8, 0.8, 0.8])

    #add coast lines 
    ax.coastlines(resolution='50m')

    #unpacking tuple
    min, max = minmax

    #ticks
    gl = ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
    gl.top_labels=False #suppress top labels
    gl.right_labels=False #suppress right labels
    gl.rotate_labels=False
    gl.ylocator = mticker.FixedLocator([50, 55, 60, 65, 70, 75, 80])
    gl.xlocator = mticker.FixedLocator([-10, -20, -30, -40, -50, -60, -70, -80, -90])
    gl.xlabel_style = {'size': 9}
    gl.ylabel_style = {'size': 9}

    #plotting
    p1 = ax.pcolormesh(ds.nav_lon_grid_T, ds.nav_lat_grid_T, vel, transform=ccrs.PlateCarree(), vmin=min, vmax=max, cmap='cividis')
    ax_cb = plt.axes([0.88, 0.25, 0.022, 0.5])
    cb = plt.colorbar(p1,cax=ax_cb, orientation='vertical')#, format='%.0e')
    cb_name = "Velocity ($m$ $s^{-1}$)"
    cb.ax.set_ylabel(cb_name)

    #plotting arrows
    n = 3 #slicing data (bigger slices = fewer and bigger arrows)
    Y = ds.nav_lat_grid_T.to_numpy()
    X = ds.nav_lon_grid_T.to_numpy()
    U = ds.U.to_numpy()
    V = ds.V.to_numpy()
    ax.quiver(X[::n,::n],Y[::n,::n],U[::n,::n],V[::n,::n],transform=ccrs.PlateCarree(),color="red")
    #quiv = ds.plot.quiver(x='nav_lon_grid_T', y='nav_lat_grid_T', ax=ax, u='U', v='V', transform=ccrs.PlateCarree())#, width=0.007 ,headaxislength=3,headlength=4, headwidth=3, scale=5, colors="white")
    #plt.quiverkey(quiv, 

    #title
    titl = "Current velocity in the top " + str(d) + "m of the Labrador Sea, " + run1 #not including mask because it should be LS not LS2k or LSCR
    ax.set_title(titl,fontdict={'fontsize': 12})

    #save and close figure
    name = "pics_currentVel/" + run1 + "_currentVel_map_" + mask + str(d) + ".png"
    plt.savefig(name,dpi=300, bbox_inches="tight")
    plt.clf()

if __name__ == "__main__":
    mapCurrentVelocities(mask='LS',run1='EPM151',d=50)
    mapCurrentVelocities(mask='LS',run1='EPM151',d=200)
    mapCurrentVelocities(mask='LS',run1='EPM151',d=1000)
    mapCurrentVelocities(mask='LS',run1='EPM151',d=2000)

    mapCurrentVelocities(mask='LS',run1='EPM152',d=50)
    mapCurrentVelocities(mask='LS',run1='EPM152',d=200)
    mapCurrentVelocities(mask='LS',run1='EPM152',d=1000)
    mapCurrentVelocities(mask='LS',run1='EPM152',d=2000)

    mapCurrentVelocities(mask='LS',run1='EPM155',d=50)
    mapCurrentVelocities(mask='LS',run1='EPM155',d=200)
    mapCurrentVelocities(mask='LS',run1='EPM155',d=1000)
    mapCurrentVelocities(mask='LS',run1='EPM155',d=2000)

    mapCurrentVelocities(mask='LS',run1='EPM156',d=50)
    mapCurrentVelocities(mask='LS',run1='EPM156',d=200)
    mapCurrentVelocities(mask='LS',run1='EPM156',d=1000)
    mapCurrentVelocities(mask='LS',run1='EPM156',d=2000)

    mapCurrentVelocities(mask='LS',run1='EPM157',d=50)
    mapCurrentVelocities(mask='LS',run1='EPM157',d=200)
    mapCurrentVelocities(mask='LS',run1='EPM157',d=1000)
    mapCurrentVelocities(mask='LS',run1='EPM157',d=2000)

    mapCurrentVelocities(mask='LS',run1='EPM158',d=50)
    mapCurrentVelocities(mask='LS',run1='EPM158',d=200)
    mapCurrentVelocities(mask='LS',run1='EPM158',d=1000)
    mapCurrentVelocities(mask='LS',run1='EPM158',d=2000)
#CBlabel = 'MLD depth ($m$)'
#
#if mask == 'LS2k': mask_description = ' interior'
#elif mask == 'LS': mask_description = ''
#elif mask == 'LSCR': mask_description = ' convection region'
#    
#if variable=='max_MLD': title = 'Difference of the max mixed layer depth in \nthe Labrador Sea' + mask_description + ', ' + run1 + '-' + run2
#if variable=='avg_MLD': title = 'Difference of the  average mixed layer depth in \nthe Labrador Sea' + mask_description + ', ' + run1 + '-' + run2
#
#fileName  = 'pics_MLD/' + run1 + '-' + run2 + '_' + variable + '_map_' + mask
#LSmap.LSmap(da,da.nav_lon_grid_T,da.nav_lat_grid_T,minmax,CBlabel,title,fileName)#,scale='log')
##
