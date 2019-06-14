#!/bin/bash
#$ -hard -l pamcrash1=38
#$ -q pamcrash1@*
#$ -soft -q pamcrash1@mb-so4.cax.lan
#$ -cwd -V
#$ -j y
#$ -N SK3165EUB_BIU_003_001_103_003_2015
#$ -p -50
#$ -ac popis_ulohy=-
#$ -a 06141213
#$ -M frantisek.siegl@idiada.cz
#$ -m bes
scratch_dir=/scr1/scratch/grid/siegl/$JOB_NAME.$JOB_ID
cd $scratch_dir

/bin/uname -a

echo "Starting PamCrash"
export PAM_LMD_LICENSE_FILE=7789@mb-dc1
export PAMHOME=/usr1/applications/pamcrash/v2015.03/pamcrash_safe/
/usr1/applications/pamcrash/v2015.03/pamcrash_safe/2015.03/pamworld -np 0 -lic CRASHSAF  SK3165EUB_BIU_003_001_103_003_2015.pc > SK3165EUB_BIU_003_001_103_003_2015.pc.out
echo "PamCrash finished"
