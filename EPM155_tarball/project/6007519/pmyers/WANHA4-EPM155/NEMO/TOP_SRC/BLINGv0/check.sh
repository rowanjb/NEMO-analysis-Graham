#!/bin/bash
for i in *F90
do
   echo $i
   diff $i /scratch/castrode/CONFIG_ANHA4/ANHA4-ELC010/TOP_SRC/BLINGv0/$i
done
