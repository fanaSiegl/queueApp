#!/bin/bash
#$ -hard -l pamcrash1=38 -l excl=true -l hostname=mb-so4.cax.lan
#$ -q pamcrash1@*
#$ -cwd -V
#$ -j y
#$ -N SK3165EUB_BIU_003_001_103_003_2015
#$ -p -50
#$ -ac popis_ulohy=-
#$ -a 02051753
#$ -M frantisek.siegl@idiada.cz
#$ -m beas
scratch_dir=/scr1/scratch/grid/siegl/$JOB_NAME.$JOB_ID
cd $scratch_dir

/bin/uname -a

echo "Starting PamCrash"
export PAM_LMD_LICENSE_FILE=7789@mb-dc1
export PAMHOME=/usr1/applications/pamcrash/v2015.03/pamcrash_safe/
/usr1/applications/pamcrash/v2015.03/pamcrash_safe/2015.03/pamworld -np 32 -lic CRASHSAF  SK3165EUB_BIU_003_001_103_003_2015.pc > SK3165EUB_BIU_003_001_103_003_2015.pc.out
echo "PamCrash finished with the status:" $?

# now sleep
sleep 10

# postprocessing - META
metaSessionName=/data/fem/+software/SKRIPTY/tools/python/metaTools/SESSION/PAMCRASH_IMPACT/META_queue_session.ses
if [ -r $metaSessionName -a -f /usr1/applications/ansa/BETA_CAE_Systems/meta_post_v19.1.1/meta_post64.sh ]; then
    echo "Starting META postprocessing"
    echo "Starting META postprocessing" >> SK3165EUB_BIU_003_001_103_003_2015.log
    /usr1/applications/ansa/BETA_CAE_Systems/meta_post_v19.1.1/meta_post64.sh -b -foregr -virtualx_64bit -s $metaSessionName SK3165EUB_BIU_003_001_103_003_2015 &>> SK3165EUB_BIU_003_001_103_003_2015.log
    sleep 5
    echo "META postprocessing finished"
    echo "META postprocessing finished" >> SK3165EUB_BIU_003_001_103_003_2015.log
fi
