#Throw-away script for making sections for later calculations (i.e., transports, cross sections)

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

#for making a map to visualize the sections
westLon = -70 #-90
eastLon = -40 #-10 -35
northLat = 70 #85
southLat = 50 #35

#for comparison reasons
#ii, jj = tp.section_calculation(174, 199, 330, 308)

#LS2k section #####################################################################################################################

#getting some starting data to play with
mask = xr.open_dataarray('mask_LS_2k.nc').astype(int)
mask = mask[:,:,0]

#for getting the perimeter cells (i.e., the edge cells in a mask of where LS depth > 2000 m)
#this is done by first adding the cells with neighbours above, below, left, and right 
#       concentric mask   one cell lower   one cell higher   one cell left    one cell right
mask2 = mask[1:-1,1:-1] + mask[:-2,1:-1] + mask[2:,1:-1]   + mask[1:-1,:-2] + mask[1:-1,2:]

#filtering
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
#(this is hacky, but it's a one-off, so I can forgive myself)
lat = coords[0][0]
lon = coords[0][1]
j = ids[0][0]
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

#saving the coordinates
lats = sorted_coords[:,0]
lons = sorted_coords[:,1]
sorted_ids = sorted_ids + 1
id_lats = sorted_ids[:,0]
id_lons = sorted_ids[:,1]
np.savetxt("LS2k_section_lats.csv", lats, fmt='%s', delimiter=",")
np.savetxt("LS2k_section_lons.csv", lons, fmt='%s', delimiter=",")
np.savetxt("LS2k_section_idy.csv", id_lats.astype(int), fmt='%s', delimiter=",")
np.savetxt("LS2k_section_idx.csv", id_lons.astype(int), fmt='%s', delimiter=",")

#OSNAP west section ##########################################################################################################################

#vertices (from another one of Tahya's scripts)
iLogOri = [170, 190, 199, 212, 220, 223]
jLogOri = [329, 332, 337, 372, 376, 379]

#getting the fill lists of coordinates and indices associated with the vertices
lats = []
lons = []
lats_id = []
lons_id = []
for n in range(len(iLogOri)-1):

    ii,jj = tp.section_calculation(iLogOri[n], jLogOri[n], iLogOri[n+1], jLogOri[n+1])
    
    lats_id = np.append(lats_id, jj)
    lons_id = np.append(lons_id, ii)

    for nn,x in enumerate(ii):
        y = jj[nn]
        lat = mask.nav_lat_grid_T[y,x].to_numpy()
        lon = mask.nav_lon_grid_T[y,x].to_numpy()
        lats = np.append(lats,lat)
        lons = np.append(lons,lon)

#saving the lists
lats_id = np.reshape(lats_id,(len(lats_id),1))
lons_id = np.reshape(lons_id,(len(lons_id),1))
osnap_section = np.hstack((lats_id,lons_id))
np.savetxt("osnap_section.csv", osnap_section.astype(int), fmt='%s', delimiter=",")

#plotting ###################################################################################################################################

#loading the 2000m isobath section
lats = np.loadtxt('LS2k_section_lats.csv')
lons = np.loadtxt('LS2k_section_lons.csv')
lats_short = []
lons_short = []
for i in [0,12,26,40,60,67,85,99,114,124,-9,-5,-1]:
    lats_short = np.append(lats_short,lats[i]) #[::15]
    lons_short = np.append(lons_short,lons[i]) #[::15]

##WGC section
#lats_short = lats_short[-6:]
#lons_short = lons_short[-6:]
#print(lats_short)
#print(lons_short)
#quit()

##LC section
#lats_short = lats_short[:6]
#lons_short = lons_short[:6]
#print(lats_short)
#print(lons_short)

#Bottom section
lats_short = [53, 53, 58.669487]
lons_short = [-51.4991684, -43, -43]

#loading the osnap section
#lons_id, lats_id = np.loadtxt('osnap_section.csv',delimiter=',',unpack=True)
#lons_id = lons_id.astype(int)
#lats_id = lats_id.astype(int)
#lats_short = []
#lons_short = []
#for i in range(len(lons_id)):
#    lat = mask.nav_lat_grid_T[lons_id[i],lats_id[i]].to_numpy()
#    lats_short = np.append(lats_short,lat)
#    lon = mask.nav_lon_grid_T[lons_id[i],lats_id[i]].to_numpy()
#    lons_short = np.append(lons_short,lon)

#AR7W section
#UNCOMMENT THESE TO PLOT THE AR7W SECTION
##lons_short = [-55.033333, -48.250000]
##lats_short = [54.750000, 60.533333]


#np.savetxt("LS2k_section_short_lats.csv", lats_short, fmt='%s', delimiter=",")
#np.savetxt("LS2k_section_short_lons.csv", lons_short, fmt='%s', delimiter=",")

##I THINK THIS IS DELETABLE
##but it might not be
#for n,i in enumerate(lons_id):
#    j = lats_id[n]
#    mask = xr.where( (mask.x_grid_T == i) & (mask.y_grid_T == j), mask + 10, mask)
#
#mask = mask.where(mask>1, drop=True)
#mask = xr.where(mask>0,1,0)
#print(mask)
#print(mask.sum().to_numpy())
#print(len(lats_id))
#quit()
#
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

mask = mask.where(mask>0,drop=True)

#plotting
p1 = ax.pcolormesh(mask.nav_lon_grid_T.to_numpy(), mask.nav_lat_grid_T.to_numpy(), mask.to_numpy(), transform=ccrs.PlateCarree(), cmap=cm)
p2 = ax.plot(lons_short,lats_short,'.-',color='red',linewidth=3,markersize=2,transform=ccrs.PlateCarree())
#p3 = ax.plot(lons_short,lats_short,'.-',linewidth=0.3,markersize=0.3,transform=ccrs.PlateCarree())
#(lons, lats, '.-', linewidth=0.5, markersize=2,  transform=ccrs.PlateCarree()) #mask.nav_lon_grid_T[1:-1,1:-1], mask.nav_lat_grid_T[1:-1,1:-1], mask2, transform=ccrs.PlateCarree(), cmap=cm)
#ax_cb = plt.axes([0.88, 0.25, 0.022, 0.5])
#cb = plt.colorbar(p1,cax=ax_cb, orientation='vertical')#, format='%.0e')
#cb.formatter.set_powerlimits((0, 0))
#cb.ax.set_ylabel(CBlabel)

#title='LS2k section'
fileName='section_LSsouth'

#title
#ax.set_title(title)# + ' ' + date)#,fontdict={'fontsize': 12})

#save and close figure
plt.savefig(fileName + '.png',dpi=2400, bbox_inches="tight")
plt.clf()
print('done')                    
