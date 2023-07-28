#creates cross sections from NEMO output
#annoyinly only uses nearest neighbour, not interp. (fix this!??)

import os
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import datetime
import matplotlib.dates as mdates

import metpy.calc as mpcalc
from metpy.cbook import get_test_data
from metpy.interpolate import cross_section
from metpy.interpolate import geodesic
import pyproj
import xoak

def crossSectionEngine(da,vertices_lat,vertices_lon):

    da.xoak.set_index(['lat', 'lon'], 'scipy_kdtree')
    wgs84 = pyproj.CRS(4326)

    for i in range(len(vertices_lat)-1): #looping through each subsection and combining the resulting cross sections into one
        
        start = (vertices_lat[i], vertices_lon[i]) #starting vertex
        end = (vertices_lat[i+1], vertices_lon[i+1]) #ending vertex
        path = geodesic(wgs84, start, end, steps=25) #getting "steps" number of points on the path between start and end 
        
        cross = da.xoak.sel( #getting the cross section (i.e., values at each poin on the path and at each depth)
                lat=xr.DataArray(path[:, 1], dims='index', attrs=da.lat.attrs),
                lon=xr.DataArray(path[:, 0], dims='index', attrs=da.lon.attrs)
        )

        #getting distances from starting vertex and angles from reference meridian of each point
        geod = pyproj.Geod(ellps='sphere') #use pyproj.Geod class
        distances = []
        forward_azimuth = []
        for ii in path:
                az12, __, dist = geod.inv(vertices_lon[i],vertices_lat[i],ii[0],ii[1])
                distances = np.append(distances,dist)
                forward_azimuth = np.append(forward_azimuth, az12)
        forward_azimuth[0] = forward_azimuth[1] #the first element is always 180
        forward_azimuth = np.radians(forward_azimuth)

        ##note: the cross sections are sometimes inclusive of the ends
        #cross = cross[:,1:]
        #distances = distances[1:]

        if i == 0: #if this is the first subsection...
                cross = cross.assign_coords(dists=('index',distances)) #add distances to the cross section 
                cross = cross.assign_coords(forward_azimuth=('index',forward_azimuth)) #and forward azimuth
                full_cross = cross #and initialize the full cross section dataarray
        else: #if this is not the first subsection...
                distances = distances + full_cross.dists[-1].to_numpy() #add distance to the first subsection vertex
                cross = cross.assign_coords(dists=('index',distances)) #then add distances to the cross section
                cross = cross.assign_coords(forward_azimuth=('index',forward_azimuth)) #and forward azimuth
                full_cross = xr.concat([full_cross, cross], dim='index') #and append to the full cross section dataarray

    return full_cross

def crossSectionGridT(variable,run,section):
    """Creates cross section of a variable using nearest neighbour. 
    
            Parameters:
                    variable:	'vosaline' (salinity), 'votemper' (temperature), etc.
                    run:		'EPM151' etc.
                    section:	'OSNAP' or 'AR7W'
            Returns:
                    DataArray of cross section
    """

    gridT_txt = run + '_filepaths/' + run + '_gridT_filepaths.txt'
    with open(gridT_txt) as f: lines = f.readlines()
    paths = [line.strip() for line in lines][:3]
    preprocessor = lambda ds: ds[[variable]]
    ds = xr.open_mfdataset(paths, preprocess = preprocessor)
    da = ds[variable]
    da = da.rename({'deptht': 'z', 'x_grid_T': 'x', 'y_grid_T': 'y', 'nav_lat_grid_T': 'lat', 'nav_lon_grid_T': 'lon'})

    if section == 'OSNAP':
            iLogOri = [170, 190, 199, 212, 220, 223] #osnap vertices
            jLogOri = [329, 332, 337, 372, 376, 379]
            #vertices_lon = [-57.007767, -51.974033, -49.78329, -47.538982, -45.512913, -44.8054]
            #vertices_lat = [52.07664, 52.875805, 53.789803, 59.202328, 59.93713, 60.424892]
            vertices_lon = da.lon[jLogOri[0], iLogOri[0]].to_numpy() #converting to coordinates
            vertices_lat = da.lat[jLogOri[0], iLogOri[0]].to_numpy()
            for n in range(len(iLogOri)-1):
                    next_lon = da.lon[jLogOri[n+1], iLogOri[n+1]].to_numpy()
                    vertices_lon = np.append(vertices_lon, next_lon)
                    next_lat = da.lat[jLogOri[n+1], iLogOri[n+1]].to_numpy()
                    vertices_lat = np.append(vertices_lat, next_lat)
    #elif section == 'AR7W': 
            #define vertices here

    da = da.where( (da.y > 250) & (da.y < 500) & (da.x > 100) & (da.x < 250), drop=True)
    da = da.mean(dim='time_counter')

    return crossSectionEngine(da,vertices_lat,vertices_lon)

def crossSectionVelocity(run,section):
    """Creates cross section velocity using nearest neighbour. 
    
            Parameters:
                    run:            'EPM151' etc.
                    section:        'OSNAP' or 'AR7W'
            Returns:
                    DataArray of cross section
    """

    gridU_txt = run + '_filepaths/' + run + '_gridU_filepaths.txt'
    gridV_txt = run + '_filepaths/' + run + '_gridV_filepaths.txt'
    gridT_txt = run + '_filepaths/' + run + '_gridT_filepaths.txt'

    with open(gridU_txt) as f: lines = f.readlines()
    pathsU = [line.strip() for line in lines][:3]
    with open(gridV_txt) as f: lines = f.readlines()
    pathsV = [line.strip() for line in lines][:3]
    with open(gridT_txt) as f: lines = f.readlines()
    pathsT = [line.strip() for line in lines][:3]

    preprocessorU = lambda ds: ds[['vozocrtx']]
    preprocessorV = lambda ds: ds[['vomecrty']]
    preprocessorT = lambda ds: ds[['vosaline']] #temporary placeholder

    dsu = xr.open_mfdataset(pathsU, preprocess = preprocessorU)
    dsv = xr.open_mfdataset(pathsV, preprocess = preprocessorV)
    dst = xr.open_mfdataset(pathsT, preprocess = preprocessorT)
    
    dau = dsu['vozocrtx']
    dav = dsv['vomecrty']        
    dat = dst['vosaline']
    
    dau = dau.rename({'depthu': 'z', 'nav_lat': 'lat', 'nav_lon': 'lon'})
    dav = dav.rename({'depthv': 'z', 'nav_lat': 'lat', 'nav_lon': 'lon'})
    dat = dat.rename({'deptht': 'z', 'x_grid_T': 'x', 'y_grid_T': 'y', 'nav_lat_grid_T': 'lat', 'nav_lon_grid_T': 'lon'})

    if section == 'OSNAP':
            iLogOri = [170, 190, 199, 212, 220, 223] #osnap vertices
            jLogOri = [329, 332, 337, 372, 376, 379]
            #vertices_lon = [-57.007767, -51.974033, -49.78329, -47.538982, -45.512913, -44.8054]
            #vertices_lat = [52.07664, 52.875805, 53.789803, 59.202328, 59.93713, 60.424892]
            vertices_lon = dat.lon[jLogOri[0], iLogOri[0]].to_numpy() #converting to coordinates
            vertices_lat = dat.lat[jLogOri[0], iLogOri[0]].to_numpy()
            for n in range(len(iLogOri)-1):
                    next_lon = dat.lon[jLogOri[n+1], iLogOri[n+1]].to_numpy()
                    vertices_lon = np.append(vertices_lon, next_lon)
                    next_lat = dat.lat[jLogOri[n+1], iLogOri[n+1]].to_numpy()
                    vertices_lat = np.append(vertices_lat, next_lat)
    #elif section == 'AR7W': 
            #define vertices here

    dau = dau.where( (dau.y > 250) & (dau.y < 500) & (dau.x > 100) & (dau.x < 250), drop=True)
    dav = dav.where( (dav.y > 250) & (dav.y < 500) & (dav.x > 100) & (dav.x < 250), drop=True)
    dat = dat.where( (dat.y > 250) & (dat.y < 500) & (dat.x > 100) & (dat.x < 250), drop=True)

    #to-do
    #co-locate the velocities on the t grid
    #add to the t grid
    #remove salinity so that it's a da
    #continue the rest of the function like the one above		

    #first, velocities are co-located on the T grid:
    #(note x and y aren't needed as new variables, so they're dropped)
    dau = dau.interp(x=dau.x+0.5).drop_vars('x')
    dav = dav.interp(y=dav.y-0.5).drop_vars('y')
    
    dau['lat'] = dat.lat
    dau['lon'] = dat.lon
    dav['lat'] = dat.lat
    dav['lon'] = dat.lon

    dau = dau.mean(dim='time_counter')
    dav = dav.mean(dim='time_counter')

    dau_fullCross = crossSectionEngine(dau,vertices_lat,vertices_lon)
    dav_fullCross = crossSectionEngine(dav,vertices_lat,vertices_lon)

    u_projected = dau_fullCross*np.cos(dau_fullCross.forward_azimuth)
    v_projected = dav_fullCross*np.sin(dav_fullCross.forward_azimuth)

    crossSectionVelocity = u_projected + v_projected
    print(crossSectionVelocity)
    quit()

    #da = ((dau**2) + (dav**2))**0.5
    dat = dat.assign_coords(u=dau)
    dat = dat.assign_coords(v=dav)
    print(dat)
    quit()

    dat = dat.reset_coords('velocity')
    #dat = dat.drop('vosaline')
    #print(dat)
    #dat = dat.to_array()
    dat = dat.velocity
    dat = dat.mean(dim='time_counter')
    
    dat.xoak.set_index(['lat', 'lon'], 'scipy_kdtree')
    wgs84 = pyproj.CRS(4326)

    for i in range(len(vertices_lat)-1): #looping through each subsection and combining the resulting cross sections into one

        start = (vertices_lat[i], vertices_lon[i]) #starting vertex
        end = (vertices_lat[i+1], vertices_lon[i+1]) #ending vertex
        path = geodesic(wgs84, start, end, steps=25) #getting "steps" number of points on the path between start and end 

        cross = dat.xoak.sel( #getting the cross section (i.e., values at each poin on the path and at each depth)
                lat=xr.DataArray(path[:, 1], dims='index', attrs=dat.lat.attrs),
                lon=xr.DataArray(path[:, 0], dims='index', attrs=dat.lon.attrs)
        )

        #getting distances from starting vertex and angles from reference meridian of each point
        geod = pyproj.Geod(ellps='sphere') #use pyproj.Geod class
        distances = []
        forward_azimuth = []
        for ii in path:
                az12, __, dist = geod.inv(vertices_lon[i],vertices_lat[i],ii[0],ii[1])
                distances = np.append(distances,dist)
                forward_azimuth = np.append(forward_azimuth, az12)
        forward_azimuth[0] = forward_azimuth[1] 
        

        ##note: the cross sections are sometimes inclusive of the ends
        #cross = cross[:,1:]
        #distances = distances[1:]
    
        if i == 0: #if this is the first subsection...
                cross = cross.assign_coords(dists=('index',distances)) #add distances to the cross section 
                cross = cross.assign_coords(forward_azimuth=('index',forward_azimuth)) #and forward azimuth
                full_cross = cross #and initialize the full cross section dataarray
        else: #if this is not the first subsection...
                distances = distances + full_cross.dists[-1].to_numpy() #add distance to the first subsection vertex
                cross = cross.assign_coords(dists=('index',distances)) #then add distances to the cross section
                cross = cross.assign_coords(forward_azimuth=('index',forward_azimuth)) #and forward azimuth
                full_cross = xr.concat([full_cross, cross], dim='index') #and append to the full cross section dataarray
    
    #projecting...
    return full_cross



if __name__ == "__main__":
    #crossV = crossSection(variable='vomecrty',run='EPM151',section='OSNAP')
    #crossU = crossSection(variable='vozocrtx',run='EPM151',section='OSNAP')
    #crossS = crossSectionGridT(variable='vosaline',run='EPM151',section='OSNAP')
    crossVel = crossSectionVelocity('EPM151','OSNAP')

    print(crossVel.forward_azimuth.to_numpy())

    #full_cross.to_netcdf(run + '_crossSection/' + run + '_' + variable + '.nc')
