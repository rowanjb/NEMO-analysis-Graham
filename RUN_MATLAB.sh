#!/bin/bash 
##SBATCH --account=rrg-pmyers-ad,
##SBATCH --ntasks=1                # number of tasks
##`SBATCH --cpus-per-task=1         # number of cores per task (adjust this when using PCT)
##SBATCH --mem-per-cpu=4000M       # memory; default unit is megabytes 
##SBATCH --time=00-24:05            # time (DD-HH:MM) 
##SBATCH --input=CalculateFluxes.m # input file
##SBATCH --output=matlab_test.log  # output file
##SBATCH --mail-type=ALL
##SBATCH --mail-user=ridenour@ualberta.ca

#SBATCH -J TransportJob_ANHA12_Labrador_53N
#SBATCH --ntasks=1
#SBATCH --mem=16000
#SBATCH --account=rrg-pmyers-ad
##SBATCH -t 00-10:00        ## 0 day, 1 hour, 0 minutes
#SBATCH -t 00-4:00        ## 0 day, 1 hour, 0 minutes
#SBATCH -t 00-72:00        ## 0 day, 1 hour, 0 minutes
##SBATCH --input=CalculateFluxes.m # input file
#SBATCH --input=CalculateFluxes-EXH006-LabradorZonal53NIndex.m # input file
#SBATCH -o slurm-mem-%j.out
#SBATCH -e slurm-mem-%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=rowan2@ualberta.ca
module load matlab/2020a
srun matlab -nodisplay -nosplash -nojvm -singleCompThread

