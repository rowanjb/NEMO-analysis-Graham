#!/bin/bash
##^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^##
##         run python in a job on graham with Slurm                   ##
##            (May07, 2021: weissgib@ualberta.ca)                     ##
##          Copied 27 Feb 2023 by rowan2@ualberta.ca                  ##
##^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^##
#SBATCH -A rrg-pmyers-ad
#SBATCH -J EKE_EPM151 
#SBATCH --ntasks=1
#SBATCH --mem=60000
#SBATCH -t 0-10:00 
#SBATCH -o slurm-mem-%j.out
#SBATCH -e slurm-mem-%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=rowan2@ualberta.ca

module load StdEnv/2020 gcc/9.3.0
module load gdal/3.5.1 
module load python/3.10

source /home/rowan/snakes2/bin/activate
python /home/rowan/projects/rrg-pmyers-ad/rowan/NEMO-analysis-Graham/EKE.py
