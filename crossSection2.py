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

file_suffix = {
	'vosaline': 'gridT.nc',
	'votemper': 'gridT.nc',
	'vozocrtx': 'gridU.nc',
	'vomecrty': 'gridV.nc'
}

to_rename = {
	'deptht': 'z',
	'depthu': 'z',
	'depthv': 'z',
	'x_grid_T': 'x',
	'y_grid_T': 'y',
	'nav_lat_grid_T': 'lat',
	'nav_lon_grid_T': 'lon',
	'nav_lat': 'lat',
	'nav_lon': 'lon'
}

def crossSection(variable,run,section):
	"""Creates cross section of a variable using nearest neighbour. 
        
                Parameters:
                        variable:	'vosaline' (salinity), 'votemper' (temperature), etc.
                	run:		'EPM151' etc.
			section:	'OSNAP' or 'AR7W'
		Returns:
                        DataArray of cross section
        """

	pauls_nemo_dir = '/mnt/storage6/myers/NEMO/ANHA4-'
	folder_path = pauls_nemo_dir + run + '/' 
	paths = sorted([folder_path + file for file in os.listdir(folder_path) if file.endswith(file_suffix[variable])])[:3]
	preprocessor = lambda ds: ds[[variable]]
	ds = xr.open_mfdataset(paths, preprocess = preprocessor)
	da = ds[variable]
	elif variable == 'velocity':
		pathsU = sorted([folder_path + file for file in os.listdir(folder_path) if file.endswith(file_suffix['vozocrtx'])])[:3]
		pathsV = sorted([folder_path + file for file in os.listdir(folder_path) if file.endswith(file_suffix['vomecrty'])])[:3]
		pathsT = sorted([folder_path + file for file in os.listdir(folder_path) if file.endswith(file_suffix['vosaline'])])[:3]
		preprocessorU = lambda ds: ds[['vozocrtx']]
		preprocessorV = lambda ds: ds[['vomecrty']]
		preprocessorT = lambda ds: ds[['vosaline']]
		dsu = xr.open_mfdataset(pathsU, preprocess = preprocessorU)
		dsv = xr.open_mfdataset(pathsV, preprocess = preprocessorV)
                preprocessorT = lambda ds: ds[['vosaline']]
		dau = dsu['vozocrtx']
		dav = dsv['vomecrty'] 

	for item in to_rename.items():
		try:
			da = da.rename({item[0]: item[1]})
		except Exception:
			pass

	if section == 'OSNAP':
		iLogOri = [170, 190, 199, 212, 220, 223] #osnap vertices
		jLogOri = [329, 332, 337, 372, 376, 379]
		vertices_lon = [-57.007767, -51.974033, -49.78329, -47.538982, -45.512913, -44.8054]
		vertices_lat = [52.07664, 52.875805, 53.789803, 59.202328, 59.93713, 60.424892]
		#vertices_lon = da.lon[jLogOri[0], iLogOri[0]].to_numpy() #converting to coordinates
		#vertices_lat = da.lat[jLogOri[0], iLogOri[0]].to_numpy()
		#for n in range(len(iLogOri)-1):
			#next_lon = da.lon[jLogOri[n+1], iLogOri[n+1]].to_numpy()
			#vertices_lon = np.append(vertices_lon, next_lon)
			#next_lat = da.lat[jLogOri[n+1], iLogOri[n+1]].to_numpy()
			#vertices_lat = np.append(vertices_lat, next_lat)
	#elif section == 'AR7W': 
		#define vertices here

	da = da.where( (da.y > 250) & (da.y < 500) & (da.x > 100) & (da.x < 250), drop=True)
	da = da.mean(dim='time_counter')
	da.xoak.set_index(['lat', 'lon'], 'scipy_kdtree')
	wgs84 = pyproj.CRS(4326)

	for i in range(len(vertices_lat)-1): #looping through each subsection and combining the resulting cross sections into one

		start = (vertices_lat[i], vertices_lon[i]) #starting vertex
		end = (vertices_lat[i+1], vertices_lon[i+1]) #ending vertex
		path = geodesic(wgs84, start, end, steps=25) #getting "steps" number of points on the path between start and end 

		print(path)

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

def orthoVel(crossU,crossV):
	"""Calculates velocity component perpindicular to a section.
        
                Parameters:
                        crossU:		cross section u velocity
			crossV 		cross section v velocity
                Returns:
                        DataArray of velocity 
        """

	#print(crossU.lat.to_numpy())
	#print(crossV.lat.to_numpy())

if __name__ == "__main__":
	crossV = crossSection(variable='vomecrty',run='EPM151',section='OSNAP')
	crossU = crossSection(variable='vozocrtx',run='EPM151',section='OSNAP')
	#crossS = crossSection(variable='vosaline',run='EPM151',section='OSNAP')
	
	orthoVel(crossU,crossV)

	#full_cross.to_netcdf(run + '_crossSection/' + run + '_' + variable + '.nc')
