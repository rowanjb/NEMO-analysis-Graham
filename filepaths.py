#get list of files that don't give "all nan slice" errors
#Rowan Brown
#May 8, 2023

import xarray as xr
import os

#run
run = 'EPM158'

#directory of nemo output files on graham
nemo_output_dir = '/home/rowan/projects/rrg-pmyers-ad/pmyers/ANHA4/ANHA4-' + run + '-S/'

#list of filepaths
filepaths_gridT = sorted([nemo_output_dir + file for file in os.listdir(nemo_output_dir) if file.endswith('gridT.nc')])#[::300]
filepaths_gridU = sorted([nemo_output_dir + file for file in os.listdir(nemo_output_dir) if file.endswith('gridU.nc')])#[::300]
filepaths_gridV = sorted([nemo_output_dir + file for file in os.listdir(nemo_output_dir) if file.endswith('gridV.nc')])#[::300]
filepaths_gridB = sorted([nemo_output_dir + file for file in os.listdir(nemo_output_dir) if file.endswith('gridB.nc')])#[::300]
filepaths_gridW = sorted([nemo_output_dir + file for file in os.listdir(nemo_output_dir) if file.endswith('gridW.nc')])#[::300]
filepaths_icebergs = sorted([nemo_output_dir + file for file in os.listdir(nemo_output_dir) if file.endswith('icebergs.nc')])#[::300]
filepaths_icemod = sorted([nemo_output_dir + file for file in os.listdir(nemo_output_dir) if file.endswith('icemod.nc')])#[::300]

#testing if gridT files are read-able
bad_files = [] #initializing list of bad filepaths
for filepath in filepaths_gridT:
    try:
        DS = xr.open_dataset(filepath)
    except:
        bad_files.append(filepath) #saving any bad filepaths
        print(filepath)

#removing bad filepaths
for bad_file in bad_files:
    filepaths_gridT.remove(bad_file)
    filepaths_gridU.remove(bad_file[:-4] + 'U.nc')
    filepaths_gridV.remove(bad_file[:-4] + 'V.nc')
    filepaths_gridB.remove(bad_file[:-4] + 'B.nc')
    filepaths_gridW.remove(bad_file[:-4] + 'W.nc')
    filepaths_icebergs.remove(bad_file[:-8] + 'icebergs.nc')
    filepaths_icemod.remove(bad_file[:-8] + 'icemod.nc')

#print(filepaths_gridT)
#print(filepaths_gridU)
#print(filepaths_gridV)
#
##TEST
#bad_files.append('/home/rowan/projects/rrg-pmyers-ad/pmyers/ANHA4/ANHA4-EPM151-S/ANHA4-EPM151_y2006m02d14_gridT.nc')
#
##removing bad filepaths
#for bad_file in bad_files:
#    filepaths_gridT.remove(bad_file)
#    filepaths_gridU.remove(bad_file[:-4] + 'U.nc')
#    filepaths_gridV.remove(bad_file[:-4] + 'V.nc')
#
#print(filepaths_gridT)
#print(filepaths_gridU)
#print(filepaths_gridV)

#creating directory if doesn't already exist
dir = run + '_filepaths/'
if not os.path.exists(dir):
    os.makedirs(dir)

#saving the filepaths as txt files
with open(dir + run + '_gridT_filepaths.txt', 'w') as output:
    for i in filepaths_gridT:
        output.write(str(i) + '\n')
with open(dir + run + '_gridU_filepaths.txt', 'w') as output:
    for i in filepaths_gridU:
        output.write(str(i) + '\n')
with open(dir + run + '_gridV_filepaths.txt', 'w') as output:
    for i in filepaths_gridV:
        output.write(str(i) + '\n')
with open(dir + run + '_gridB_filepaths.txt', 'w') as output:
    for i in filepaths_gridB:
        output.write(str(i) + '\n')
with open(dir + run + '_gridW_filepaths.txt', 'w') as output:
    for i in filepaths_gridW:
        output.write(str(i) + '\n')
with open(dir + run + '_icebergs_filepaths.txt', 'w') as output:
    for i in filepaths_icebergs:
        output.write(str(i) + '\n')
with open(dir + run + '_icemod_filepaths.txt', 'w') as output:
    for i in filepaths_icemod:
        output.write(str(i) + '\n')

