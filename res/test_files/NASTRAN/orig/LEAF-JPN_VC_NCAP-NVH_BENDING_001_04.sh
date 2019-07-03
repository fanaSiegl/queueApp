#!/bin/bash
#$ -hard -l nastran=1
#$ -q nastran@*
#$ -soft -q nastran@mb-so1.cax.lan
#$ -cwd -V
#$ -N LEAF-JPN_VC_NCAP-NVH_BENDING_001_04
#$ -p -50
#$ -M pavel.hendrych@idiada.cz
#$ -m be
scratch_dir=/scr1/scratch/grid/phendrych/$JOB_NAME.$JOB_ID
cd $scratch_dir

echo "=====Spoustim nastran    --->"
/bin/uname -a
echo "====="

#/usr/applications/msc/bin/msc20055 nastran scr=yes LEAF-JPN_VC_NCAP-NVH_BENDING_001_04.bdf
#/usr1/applications/msc.2007r1/bin/msc2007 nastran scr=yes LEAF-JPN_VC_NCAP-NVH_BENDING_001_04.bdf
#/usr1/applications/msc.2008r1/bin/msc2008 nastran scr=yes LEAF-JPN_VC_NCAP-NVH_BENDING_001_04.bdf
#/usr/local/bin/nas2011 LEAF-JPN_VC_NCAP-NVH_BENDING_001_04.bdf
#/usr/local/bin/nas20141 LEAF-JPN_VC_NCAP-NVH_BENDING_001_04.bdf
/usr/local/bin/nas20171 LEAF-JPN_VC_NCAP-NVH_BENDING_001_04.bdf

sleep 10
