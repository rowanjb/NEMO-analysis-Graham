#calculates MLE for mapping and plotting purposes
#start with time-plots; expand to maps later

import os
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import datetime
import matplotlib.dates as mdates
from density import density #TEST THIS SCRIPT BEFORE OVERLY RELYING ON IT!!
import metpy.calc as mpcalc

def MLE(run,mask):

    for depth in [50,200,1000,2000]:

        ce = 0.06
        lf = 5000
        rho_o = 1025 #CHECK THIS

        dir = run + '_MLE/'
        if not os.path.exists(dir):
            os.makedirs(dir)

        gridT_txt = run + '_filepaths/' + run + '_gridT_filepaths.txt'
        ##gridU_txt = run + '_filepaths/' + run + '_gridU_filepaths.txt'
        ##gridV_txt = run + '_filepaths/' + run + '_gridV_filepaths.txt'
        with open(gridT_txt) as f: lines = f.readlines()
        filepaths_gridT = [line.strip() for line in lines]
        ##with open(gridU_txt) as f: lines = f.readlines()
        ##filepaths_gridU = [line.strip() for line in lines][:3]
        ##with open(gridV_txt) as f: lines = f.readlines()
        ##filepaths_gridV = [line.strip() for line in lines][:3]
        preprocess_gridT = lambda ds: ds[['votemper','vosaline','somxl010']] #CHECK TO MAKE SURE THIS IS THE RECOMMENDED MLD THICKNESS (WHAT DO THEY USE IN THE .F90 CODE?)
        ##preprocess_gridU = lambda ds: ds[['sozotaux']]
        ##preprocess_gridV = lambda ds: ds[['sometauy']]
        DST = xr.open_mfdataset(filepaths_gridT,preprocess=preprocess_gridT,engine="netcdf4")
        ##DSU = xr.open_mfdataset(filepaths_gridU,preprocess=preprocess_gridU,engine="netcdf4")
        ##DSV = xr.open_mfdataset(filepaths_gridV,preprocess=preprocess_gridV,engine="netcdf4")
        ##DSU = DSU.rename({'x':'x_grid_T','y':'y_grid_T'})
        #DSV = DSV.rename({'x':'x_grid_T','y':'y_grid_T'})
        
        with xr.open_dataset('masks/ANHA4_mesh_mask.nc') as DS:
            #DST = DST.assign_coords(tmask=DS.tmask[0,:,:,:])
            DST['e1t'] = DS.e1t[0,:,:].rename({'x':'x_grid_T','y':'y_grid_T'})
            DST['e2t'] = DS.e2t[0,:,:].rename({'x':'x_grid_T','y':'y_grid_T'})

        if mask == 'LS2k':
            with xr.open_dataarray('masks/mask_LS_2k.nc') as DS:
                DST = DST.assign_coords(mask=DS.astype(int))
        elif mask == 'LS':
            with xr.open_dataarray('masks/mask_LS.nc') as DS:
                DST = DST.assign_coords(mask=DS.astype(int))
        elif mask == 'LSCR':
            with xr.open_dataset('masks/ARGOProfiles_mask.nc') as DS:
                DST = DST.assign_coords(mask = DS.tmask.astype(int).rename({'x':'x_grid_T','y':'y_grid_T'}))
        else:
            print("Y'all didn't choose a mask")
            quit()

        DST = DST.where((DST.x_grid_T>100)&(DST.x_grid_T<250)&(DST.y_grid_T>300)&(DST.y_grid_T<500),drop=True)
        ##DSU = DSU.where((DSU.x_grid_T>100)&(DSU.x_grid_T<250)&(DSU.y_grid_T>300)&(DSU.y_grid_T<500),drop=True)
        ##DSV = DSV.where((DSV.x_grid_T>100)&(DSV.x_grid_T<250)&(DSV.y_grid_T>300)&(DSV.y_grid_T<500),drop=True)

        ##DSU = DSU.interp(x_grid_T=DSU.x_grid_T+0.5).drop_vars('x_grid_T') #CHECK THAT THIS INTERPOLTES ONTO THE CORRECT GRID (GRID T
        ##DSV = DSV.interp(y_grid_T=DSV.y_grid_T-0.5).drop_vars('y_grid_T')

        #without the xr.where, you get a bunch of -inf
        #ALSO, IS Z DEFINED AS NEGATIVE???
        DST['mu'] = xr.where( DST.somxl010>0, (1-((-2*DST.deptht/DST.somxl010)+1)**2) * (1+(5/21)*((-2*DST.deptht/DST.somxl010)+1)**2) , 0)
        DST['mu'] = xr.where(DST.mu>0,DST.mu,0) #taking the max of 0 and mu 
        #print(DST.deptht[10].to_numpy())
        #print(DST.mu[1,110,100,10].to_numpy())
        #print(DST.somxl010[1,110,100].to_numpy())

        omega = 7.2921e-5 #rad/s
        #tau = np.sqrt( DSU.sozotaux**2 + DSV.sometauy**2 )
        #ustar = np.sqrt( tau/rho_o )  #see page 146 of the NEMO manual v4.2.0
        #tau_sqr = DSU.sozotaux**2 + DSV.sometauy**2
        #DST['denominator'] = np.sqrt( (2*omega*np.sin(DST.nav_lat_grid_T*np.pi/180))**2 + 1/tau_sqr )

        DST['f'] = np.absolute(2*omega*np.sin(DST.nav_lat_grid_T*np.pi/180))
       
        #nabla b cross z hat
        buoyancy = density(DST.vosaline, DST.votemper)
        buoyancy = buoyancy.mean(dim='deptht')
        #instead of e1t, which is cell width, here we're getting the distances between each t-point and the t-point to the right (using interp for convenience), which is why the rightmost column is all nans
        delta_x = DST.e1t.interp(x_grid_T=DST.x_grid_T+0.5).drop_vars('x_grid_T') 
        #same as above except the distance is between each t-point and the point above it (ie distance between y_grid_T=0,x_grid_T=0 and its northern neighbour y_grid_T=1,x_grid_T=0)
        delta_y = DST.e2t.interp(y_grid_T=DST.y_grid_T+0.5).drop_vars('y_grid_T')
        delta_x = delta_x.where(delta_x.x_grid_T != 148, drop=True) #getting rid of eastmost column, which is full of nans 
        delta_y = delta_y.where(delta_y.y_grid_T != 198, drop=True) #getting rid of northernmost row, which is full of nans
        grad_x = ( buoyancy[:,:,:-2] + buoyancy[:,:,2:] )/( delta_x[:,:-1] + delta_x[:,1:] )
        grad_y = ( buoyancy[:,:-2,:] + buoyancy[:,2:,:] )/( delta_y[:-1,:] + delta_y[1:,:] )
        DST = DST.where( (DST.x_grid_T>0)&(DST.x_grid_T<148)&(DST.y_grid_T>0)&(DST.y_grid_T<198),drop=True)
        grad_x = grad_x.where( (grad_x.y_grid_T>0)&(grad_x.y_grid_T<198),drop=True)
        grad_y = grad_y.where( (grad_y.x_grid_T>0)&(grad_y.x_grid_T<148),drop=True)
        DST['bxz_i'] = grad_y
        DST['bxz_j'] = grad_x

        DST['psi_i'] = ce * DST.somxl010**2 * DST.bxz_i * DST.mu / DST.f
        DST['psi_j'] = ce * DST.somxl010**2 * DST.bxz_j * DST.mu / DST.f
        DST['psi'] = ( DST.psi_i**2 + DST.psi_j**2 )**0.5

        DST = DST.where(DST.mask > 0, drop=True)
        DST = DST.where(DST.deptht < depth, drop=True)

        psi = DST.psi.mean(dim=('x_grid_T','y_grid_T','deptht'))

        psi.to_netcdf(run + '_MLE/' + run + '_MLE_time_avg_' + mask + str(depth) + '.nc') #saving


    #buoyancy = buoyancy.rename({'x_grid_T':'x','y_grid_T':'y'})   
    #print(buoyancy)
    #print(buoyancy.get_axis_num('y_grid_T'))

    #bgrad = mpcalc.gradient( buoyancy, axes=(2,3), deltas=(delta_y,delta_x) )
    #DST['grad_b_i'] = 
    #DST['grad_b_i'] = DST.e2t #e2t is y grid, e1t is x grid
    #DST['grad_b_j'] = 
    #deptht: 50, y_grid_T: 199, x_grid_T: 149)

if __name__ == '__main__':
    MLE(run='EPM158',mask='LS')
    MLE(run='EPM158',mask='LSCR')
    MLE(run='EPM158',mask='LS2k')

