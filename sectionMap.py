import matplotlib.pyplot as plt
import matplotlib.path as mpath
import cartopy.crs as ccrs
import cartopy.feature as feature
import matplotlib.ticker as mticker
import matplotlib.colors as colors
import numpy as np
import transports as tp
import xarray as xr
import csv

westLon = -90# -70
eastLon = -10# -35
northLat = 85# 70
southLat = 35# 50

#getting the data to plot (ie the LS2k mask)
ii, jj = tp.section_calculation(174, 199, 330, 308)
mask = xr.open_dataarray('masks/mask_LS_2k.nc').astype(int)
mask = mask[:,:,0]

#masking the data to get only the perimeter cells
#this is done by first adding the cells with neighbours above, below, left, and right 
#       concentric mask   one cell lower   one cell higher   one cell left    one cell right
mask2 = mask[1:-1,1:-1] + mask[:-2,1:-1] + mask[2:,1:-1]   + mask[1:-1,:-2] + mask[1:-1,2:]
mask10 = mask2
mask2 = mask2.where(mask[1:-1,1:-1] != 0) #getting rid of non-zero cells outside the mask
mask2 = mask2.where(mask2 != 5) # wherever it's 5 we have an interior cell
mask2 = mask2.where(mask2 != 2) # wherever it's 2 we have a peninsula type cell
mask2 = mask2.where(mask2.y_grid_T > 332) #getting rid of some cells at the bottom of the mask
mask2 = mask2.where(mask2.x_grid_T < 226) #getting rid of some cells at the right of the mask
mask2 = mask2.where( (mask2.y_grid_T > 362) | (mask2.x_grid_T < 220) ) #getting rid of the remaining bottom-right cells
#two points in corners that need to be deleted from the section:
mask2 = mask2.where( (mask2.y_grid_T != 376) | (mask2.x_grid_T != 214) )
mask2 = mask2.where( (mask2.y_grid_T != 402) | (mask2.x_grid_T != 198) )

#getting the indices of the section cells 
mask3 = mask2.where(mask2>0,0)
ids = np.argwhere(mask3.values)

#getting the coordinates associated with the indices
coords = [[0,0]] 
for i in ids:
    jj = i[0] + 1
    ii = i[1] + 1
    lat = mask.nav_lat_grid_T[jj,ii].to_numpy()
    lon = mask.nav_lon_grid_T[jj,ii].to_numpy()
    coords = np.append(coords, [[lat, lon]], axis=0)
coords = np.delete(coords, 0, axis=0)

#ordering the coordinates by proximity
#(this is hacky, but it's a one-off)
lat = coords[0][0]
lon = coords[0][1]
jj = ids[0][0]
ii = ids[0][1]
sorted_ids = [[jj,ii]]
sorted_coords = [[lat,lon]]
for n,i in enumerate(coords[:-1]):
    distances = np.linalg.norm(coords-sorted_coords[n], axis=1)
    distances = [x if x != 0 else 100 for x in distances] #replace self-match
    min_id = np.argmin(distances)
    closest_coords = coords[min_id]
    closest_ids = ids[min_id]
    lat = closest_coords[0]
    lon = closest_coords[1]
    jj = closest_ids[0]
    ii = closest_ids[1]
    sorted_coords = np.append(sorted_coords, [[lat,lon]], axis=0)
    sorted_ids = np.append(sorted_ids, [[jj,ii]], axis=0)
    for nn,ii in enumerate(coords): #make the coordinates [0,0] so they don't interfere later in the loop
        la = ii[0]
        lo = ii[1]
        if la==sorted_coords[n][0] and lo==sorted_coords[n][1]:
            coords[nn] = [0,0]
    
lats = sorted_coords[:,0]
lons = sorted_coords[:,1]
sorted_ids = sorted_ids + 1
id_lats = sorted_ids[:,0]
id_lons = sorted_ids[:,1]

np.savetxt("LS2k_section_lats.csv", lats, fmt='%s', delimiter=",")
np.savetxt("LS2k_section_lons.csv", lons, fmt='%s', delimiter=",")
np.savetxt("LS2k_section_idy.csv", id_lats.astype(int), fmt='%s', delimiter=",")
np.savetxt("LS2k_section_idx.csv", id_lons.astype(int), fmt='%s', delimiter=",")

print(np.min(id_lats)-4)
print(np.max(id_lats)+4)
print(np.min(id_lons)-4)
print(np.max(id_lons)+4)

#with open("LS2k_section_lats.csv", 'w') as file:
#     writer = csv.writer(file)
#     writer.writerows(lats)
#
#with open("LS2k_section_lons.csv", 'w', newline='') as file:
#     writer = csv.writer(file)
#     writer.writerows(lons)
#
#with open("LS2k_section_idy.csv", 'w', newline='') as file:
#     writer = csv.writer(file)
#     writer.writerows(id_lats)
#
#with open("LS2k_section_idx.csv", 'w', newline='') as file:
#     writer = csv.writer(file)
#     writer.writerows(id_lons)

#for n,i in enumerate(sorted_ids):
#    idy = i[0]
#    idx = i[1]
#    print(sorted_coords[n])
#    print(mask.nav_lat_grid_T[idy,idx].to_numpy())
#    print(mask.nav_lon_grid_T[idy,idx].to_numpy())

#for n,i in enumerate(ii):
#    mask = xr.where((mask.y_grid_T==jj[n]) & (mask.x_grid_T==ii[n]),2,mask)
#mask = mask.where(mask==2)

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

#ticks
gl = ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
gl.top_labels=False #suppress top labels
gl.right_labels=False #suppress right labels
gl.rotate_labels=False
gl.ylocator = mticker.FixedLocator([50, 55, 60, 65, 70, 75, 80])
gl.xlocator = mticker.FixedLocator([-10, -20, -30, -40, -50, -60, -70, -80, -90])
gl.xlabel_style = {'size': 9}
gl.ylabel_style = {'size': 9}

#colour map
cm = 'viridis'

#plotting
#p1 = ax.pcolormesh(mask.nav_lon_grid_T[1:-1,1:-1], mask.nav_lat_grid_T[1:-1,1:-1], mask10, transform=ccrs.PlateCarree(), cmap=cm)
p2 = ax.plot(lons,lats,'.-',linewidth=0.1,markersize=0.3,transform=ccrs.PlateCarree())
#(lons, lats, '.-', linewidth=0.5, markersize=2,  transform=ccrs.PlateCarree()) #mask.nav_lon_grid_T[1:-1,1:-1], mask.nav_lat_grid_T[1:-1,1:-1], mask2, transform=ccrs.PlateCarree(), cmap=cm)
#ax_cb = plt.axes([0.88, 0.25, 0.022, 0.5])
#cb = plt.colorbar(p1,cax=ax_cb, orientation='vertical')#, format='%.0e')
#cb.formatter.set_powerlimits((0, 0))
#cb.ax.set_ylabel(CBlabel)

title='LS2k section'
fileName='Section_test'

#title
ax.set_title(title)# + ' ' + date)#,fontdict={'fontsize': 12})

#save and close figure
plt.savefig(fileName + '.png',dpi=1200, bbox_inches="tight")
plt.clf()
print('done')                    
