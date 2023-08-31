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

def LSmap(mask,minmax,fileName):

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

        #colour map
        cm = 'viridis'

        #paring down to only the mask
        #(idk why, but the plot is wrong if you don't do this)
        mask = mask.where(mask>0,drop=True)
        
        #plotting
        p1 = ax.pcolormesh(mask.nav_lon_grid_T.to_numpy(), mask.nav_lat_grid_T.to_numpy(), mask.to_numpy(), transform=ccrs.PlateCarree(), cmap=cm)

        #save and close figure
        plt.savefig(fileName + '.png',dpi=300, bbox_inches="tight")
        plt.clf

