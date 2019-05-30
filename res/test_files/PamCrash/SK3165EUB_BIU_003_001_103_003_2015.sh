#!/bin/bash
#$ -hard -l pamcrash1=26
#$ -q pamcrash1@*
#$ -soft -q pamcrash1@mb-so4.cax.lan
#$ -cwd -V
#$ -j y
#$ -N SK3165EUB_BIU_003_001_103_003_2015
#$ -p -50
#$ -ac popis_ulohy=-
#$ -a 05301509
#$ -M frantisek.siegl@idiada.cz
#$ -m bes
scratch_dir=/scr1/scratch/grid/siegl/$JOB_NAME.$JOB_ID
cd $scratch_dir
/bin/uname -a


echo "Starting PamCrash"
export PAM_LMD_LICENSE_FILE=7789@mb-dc1
export PAMHOME=/usr1/applications/pamcrash/v2015.03/pamcrash_safe/
/usr1/applications/pamcrash/v2015.03/pamcrash_safe/2015.03/pamworld -np 1 -lic CRASHSAF SK3165EUB_BIU_003_001_103_003_2015.pc  > SK3165EUB_BIU_003_001_103_003_2015.pc.out
echo "PamCrash finished"
/bin/uname -a
# now sleep until lock file disappears
sleep 30 && while [ -f SK3165EUB_BIU_003_001_103_003_2015.lck ]; do sleep 5; done

if [ -r META_queue_session.ses -a -f /usr1/applications/ansa/BETA_CAE_Systems/meta_post_v18.1.1/meta_post64.sh ]; then   #konverze do metadb
    echo "Startuji konverzi do Metadb"
    echo "Startuji konverzi do Metadb" >> SK3165EUB_BIU_003_001_103_003_2015.log
    /usr1/applications/ansa/BETA_CAE_Systems/meta_post_v18.1.1/meta_post64.sh -b -foregr -virtualx_64bit -s META_queue_session.ses SK3165EUB_BIU_003_001_103_003_2015 &>> SK3165EUB_BIU_003_001_103_003_2015.log
    sleep 5
    echo "Koncim konverzi do Metadb"
    echo "Koncim konverzi do Metadb" >> SK3165EUB_BIU_003_001_103_003_2015.log
fi
