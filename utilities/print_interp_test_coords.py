import xarray as xr

def ANHA_print_coords():
    '''Throw-away script that I made for testing how I would interpolate to get U and V 
    co-located on the t grid. It prints out some example coordinates before and after
    interpolating. Can use a distance-between-coordinates calculator to verify how far 
    apart the coordinates are. For ANHA4, they're usually within 5-10m, which seems close
    enough.'''

    #opening the t grid
    with xr.open_dataset('masks/ANHA4_mesh_mask.nc') as DS:
        tlat = DS.nav_lat
        tlon = DS.nav_lon
    
    #specifying the run
    run = 'EPM151'

    #these are text files with lists of all non-empty model outputs (made with 'filepaths.py')
    gridU_txt = run + '_filepaths/' + run + '_gridU_filepaths.txt'
    gridV_txt = run + '_filepaths/' + run + '_gridV_filepaths.txt'

    #open the text files and get lists of the .nc output filepaths
    with open(gridU_txt) as f: lines = f.readlines()
    filepaths_gridU = [line.strip() for line in lines][:3]
    with open(gridV_txt) as f: lines = f.readlines()
    filepaths_gridV = [line.strip() for line in lines][:3]

    #preprocessing (specifying variables that we need and ignoring the rest)
    preprocess_gridU = lambda ds: ds[['vozocrtx']]
    preprocess_gridV = lambda ds: ds[['vomecrty']]

    #open the datasets
    DSU = xr.open_mfdataset(filepaths_gridU,preprocess=preprocess_gridU,engine="netcdf4")
    DSV = xr.open_mfdataset(filepaths_gridV,preprocess=preprocess_gridV,engine="netcdf4")

    #renaming dimensions so that they are the same for all datasets
    DSU = DSU.rename({'depthu': 'z'})
    DSV = DSV.rename({'depthv': 'z'})

    n = 400
    m = 200

    print('U lon: ' + str( DSU.nav_lon[n,m].to_numpy() ))
    print('U lat: ' + str( DSU.nav_lat[n,m].to_numpy() ))

    print('V lon: ' + str( DSV.nav_lon[n,m].to_numpy() ))
    print('V lat: ' + str( DSV.nav_lat[n,m].to_numpy() ))

    #first, velocities are co-located on the T grid:
    DSU = DSU.interp(x=DSU.x-0.5).drop_vars('x') #changed this from +0.5 to -0.5
    DSV = DSV.interp(y=DSV.y-0.5).drop_vars('y')

    print('New U lon: ' + str( DSU.nav_lon[n,m].to_numpy() ))
    print('New U lat: ' + str( DSU.nav_lat[n,m].to_numpy() ))

    print('New V lon: ' + str( DSV.nav_lon[n,m].to_numpy() ))
    print('New V lat: ' + str( DSV.nav_lat[n,m].to_numpy() ))

    print('t lon: ' + str( tlon[n,m].to_numpy() ))
    print('t lat: ' + str( tlat[n,m].to_numpy() ))

if __name__ == '__main__':
    ANHA_print_coords()

