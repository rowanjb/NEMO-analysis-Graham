"""Useful functions for creating maps of the Labrador Sea.

        Functions:
                xrLSminmax
                LSmap
"""

import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import cartopy.crs as ccrs
import cartopy.feature as feature
import matplotlib.ticker as mticker
import matplotlib.colors as colors
import numpy as np

westLon = -70
eastLon = -40
northLat = 70
southLat = 50

#westLon = -70
#eastLon = -35
#northLat = 75
#southLat = 45

def xrLSminmax(xrData,lats,lons):
        """ Finds min and max values in xarray dataarrays (and datasets??) in the Labrador Sea.
        Principally for later use in defining a colourbar range.
        
                Parameters:
                        xrData: Dataarray containing data to be plotted
                        lats:   2D array of cell latitudes from .nc grid file
                        lons:   2D array of cell longitudes from .nc grid file
                        
                Returns:
                        Tuple containing min and max values
        """

        #define Labrador Sea region
        cond = ((lats > southLat) & (lats < northLat) & (lons < eastLon) & (lons > westLon))

        #changing masked values (which are often zero) to nan
        xrData = xrData.where(xrData!=0)
        print("Don't forget: xrLSminmax replaces 0s with NaNs; may be unphysical") 

        #find min and max values within Labrador Sea region
        max = xrData.where(cond).max(skipna=True).to_numpy()
        min = xrData.where(cond).min(skipna=True).to_numpy()

        return min, max

def LSmap(xrData,lons,lats,minmax,CBlabel,title,fileName):
        """ Saves one PNG map of Labrador Sea with data from an xarray DataArray. 
        
                Parameters:
                        xrData:         DataArray containing data to be plotted
                                        (Should contain time_counter dim of len>=1)
                        lats:           2D array of cell latitudes from .nc grid file
                        lons:           2D array of cell longitudes from .nc grid file
                        minmax:         Tuple with min and max values in the DataArray
                                        (From xrLSminmax function)
                        CBlabel:        String for the colourbar label
                        title:          String for the title (to display in the PNG)
                                        (Will have date appended to it)
                                        E.g., 'Sea surface height (EPM151)' + ' ' + date
                        fileName:       String for the name of the PNG(s)
                                        E.g., 'LS_convective_energy_EPM151_' + date + '.png'
                Returns:
                        None
        """

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

        ##ticks
        gl = ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
        gl.top_labels=False #suppress top labels
        gl.right_labels=False #suppress right labels
        gl.rotate_labels=False
        gl.xlocator = mticker.FixedLocator([-30,-35,-40,-45,-50,-55,-60,-65,-70,-75,-80])#[-10, -20, -30, -40, -50, -60, -70, -80, -90])
        gl.xlabel_style = {'size': 9}
        gl.ylabel_style = {'size': 9}
	
        ##get date
        #date = xrData["time_counter"].dt.strftime("%Y-%m-%d").to_numpy()

            p1 = xrData.plot.pcolormesh()#(
                #darray = xrData,
                #kwargs = {'transform': ccrs.PlateCarree()}
                #)#lons, lats, xrData, transform=ccrs.PlateCarree(), vmin=min, vmax=max, cmap='Greys')
            #ax_cb = plt.axes([0.78, 0.25, 0.022, 0.5])
            #cb = plt.colorbar(p1,cax=ax_cb, orientation='vertical')
            #cb.ax.set_ylabel(CBlabel)
        elif scale == 'log':
            if (min>0 and max>0) or (min<0 and max<0): #minmax range doesn't contain zero
                p1 = ax.pcolormesh(lons, lats, xrData, transform=ccrs.PlateCarree(), norm=colors.LogNorm(vmin=min, vmax=max, clip=True), cmap='gist_ncar')
                #ax_cb = plt.axes([0.78, 0.25, 0.022, 0.5])
                #cb = plt.colorbar(p1,cax=ax_cb, orientation='vertical')
                #cb.ax.set_ylabel(CBlabel)
            elif (min<0 and max>0): #minmax range contains zero
                print("Don't forget: the log scale is linearized around zero; you can play with parameters to adjust the colour bar")
                lt = 10
                p1 = ax.pcolormesh(lons, lats, xrData, transform=ccrs.PlateCarree(), cmap='gist_ncar', norm=colors.SymLogNorm(linthresh=lt, linscale=1, vmin=min, vmax=max, clip=True))
                #ax_cb = plt.axes([0.78, 0.25, 0.022, 0.5])
                #formatter = mticker.LogFormatter(base=10, labelOnlyBase=False, minor_thresholds=(50,40), linthresh=lt)
                #cb = plt.colorbar(p1,cax=ax_cb, orientation='vertical')
                #cb.ax.set_ylabel(CBlabel)
                #cb.ax.minorticks_on()
                ##minorticks = p1.norm(np.arange(0,10,1))
                ##cb.ax.yaxis.set_ticks(minorticks, minor=True)
            elif min==0 and max>0:
                print("Don't forget: the log scale is linearized just above zero; you can play with parameters to adjust the colour bar")
                lt = 10
                p1 = ax.pcolormesh(lons, lats, xrData, transform=ccrs.PlateCarree(), cmap='gist_ncar', norm=colors.SymLogNorm(linthresh=lt, linscale=1, vmin=min, vmax=max, clip=True))
                p1.set_clim(0,max)
                #ax_cb = plt.axes([0.78, 0.25, 0.022, 0.5])
                formatter = mticker.LogFormatter(base=10, labelOnlyBase=False, minor_thresholds=(50,40), linthresh=lt)
                #cb = plt.colorbar(p1,cax=ax_cb, orientation='vertical', format=formatter)
                #cb.ax.mappable.set_clim(vmin=0,vmax=max)
                #cb.ax.set_ylabel(CBlabel)
            elif max==0 and min<0:
                print("Don't forget: the log scale is linearized just below zero; you can play with parameters to adjust the colour bar")
                lt = 10
                p1 = ax.pcolormesh(lons, lats, xrData, transform=ccrs.PlateCarree(), cmap='gist_ncar', norm=colors.SymLogNorm(linthresh=lt, linscale=1, vmin=min, vmax=max, clip=True))
                p1.set_clim(0,max)
                #ax_cb = plt.axes([0.78, 0.25, 0.022, 0.5])
                formatter = mticker.LogFormatter(base=10, labelOnlyBase=False, minor_thresholds=(50,40), linthresh=lt)
                #cb = plt.colorbar(p1,cax=ax_cb, orientation='vertical', format=formatter)
                #cb.ax.mappable.set_clim(vmin=0,vmax=max)
                #cb.ax.set_ylabel(CBlabel)
            else:
                print("The chosen bounds don't work with log scale")
        else:
            print("Scale need to be 'log' or 'normal'")

        #colourbar 
        #ax_cb = plt.axes([0.78, 0.25, 0.022, 0.5])
        #cb = plt.colorbar(p1,cax=ax_cb, orientation='vertical')
        #if scale == 'log':
        #    formatter = mticker.LogFormatter(10, labelOnlyBase=False) 
        #    cb = plt.colorbar(p1,cax=ax_cb, orientation='vertical', ticks=[min,max], format=formatter)
        #cb.ax.set_ylabel(CBlabel)

        #title
        #ax.set_title(title)# + ' ' + date)#,fontdict={'fontsize': 12})

        #save and close figure
        plt.savefig(fileName + '.png',dpi=300, bbox_inches="tight")
        plt.clf
