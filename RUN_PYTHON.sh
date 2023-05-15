#!/bin/bash
##^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^##
##         run python in a job on graham with Slurm                   ##
##            (May07, 2021: weissgib@ualberta.ca)                     ##
##          Copied 27 Feb 2023 by rowan2@ualberta.ca                  ##
##^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^##
#SBATCH -A rrg-pmyers-ad
#SBATCH -J EKE_EPM151
#SBATCH --ntasks=1
#SBATCH --mem=16000
#SBATCH -t 0-10:00        ## 0 day, 2 hour, 0 minutes
#SBATCH -o slurm-mem-%j.out
#SBATCH -e slurm-mem-%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=rowan2@ualberta.ca

module load python/3.10
module load geos

source /home/rowan/snakes2/bin/activate
python /home/rowan/projects/rrg-pmyers-ad/rowan/EKE.py
