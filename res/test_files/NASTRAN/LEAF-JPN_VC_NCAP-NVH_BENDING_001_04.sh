#!/bin/bash
#$ -hard -l nastran=1 -l excl=true -l hostname=mb-so1.cax.lan
#$ -q nastran@*
#$ -cwd -V
#$ -j y
#$ -N LEAF-JPN_VC_NCAP-NVH_BENDING_001_04
#$ -p -50
#$ -ac popis_ulohy=-
#$ -a 02051835
#$ -M frantisek.siegl@idiada.cz
#$ -m beas
scratch_dir=/scr1/scratch/grid/siegl/$JOB_NAME.$JOB_ID
cd $scratch_dir

/bin/uname -a

echo "Starting NASTRAN"
/usr/local/bin/nas20171  LEAF-JPN_VC_NCAP-NVH_BENDING_001_04.bdf > LEAF-JPN_VC_NCAP-NVH_BENDING_001_04.bdf.out
echo "NASTRAN finished with the status:" $?

# now sleep
sleep 10
