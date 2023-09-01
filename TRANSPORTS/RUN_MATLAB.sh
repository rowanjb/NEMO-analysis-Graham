#!/bin/bash
##^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^##
##         run matlab in a job on graham with Slurm                   ##
##            (May07, 2021: weissgib@ualberta.ca)                     ##
##          Copied 27 Feb 2023 by rowan2@ualberta.ca                  ##
##^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^##
#SBATCH -J EPM155_Trans._ANHA4_LC2kDepth
#SBATCH --ntasks=1
#SBATCH --mem=3000
#SBATCH --account=rrg-pmyers-ad
#SBATCH -t 00-47:00 
#SBATCH --input=CalculateFluxes.m # input file
#SBATCH -o slurm-mem-%j.out
#SBATCH -e slurm-mem-%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=rowan2@ualberta.ca

module load StdEnv/2020 
module load gcc/9.3.0
module load matlab/2020b.4
srun matlab -nodisplay -nosplash -nojvm -singleCompThread

