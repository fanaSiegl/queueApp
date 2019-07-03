#!/bin/bash
#$ -hard -l nastran=1
#$ -q nastran@*
#$ -soft -q nastran@mb-so1.cax.lan
#$ -cwd -V
#$ -j y
#$ -N LEAF-JPN_VC_NCAP-NVH_BENDING_001_04
#$ -p -50
#$ -ac popis_ulohy=-
#$ -a 06171305
#$ -M frantisek.siegl@idiada.cz
#$ -m bes
scratch_dir=/scr1/scratch/grid/siegl/$JOB_NAME.$JOB_ID
cd $scratch_dir

/bin/uname -a

echo "Starting NASTRAN"
/usr/local/bin/nas20171  LEAF-JPN_VC_NCAP-NVH_BENDING_001_04.bdf > LEAF-JPN_VC_NCAP-NVH_BENDING_001_04.bdf.out
echo "NASTRAN finished"

# now sleep until lock file disappears
sleep 30 && while [ -f LEAF-JPN_VC_NCAP-NVH_BENDING_001_04.lck ]; do sleep 5; done

if [ -r META_queue_session.ses -a -f /usr1/applications/ansa/BETA_CAE_Systems/meta_post_v19.1.1/meta_post64.sh ]; then   #konverze do metadb
    echo "Startuji konverzi do Metadb"
    echo "Startuji konverzi do Metadb" >> LEAF-JPN_VC_NCAP-NVH_BENDING_001_04.log
    /usr1/applications/ansa/BETA_CAE_Systems/meta_post_v19.1.1/meta_post64.sh -b -foregr -virtualx_64bit -s META_queue_session LEAF-JPN_VC_NCAP-NVH_BENDING_001_04 &>> LEAF-JPN_VC_NCAP-NVH_BENDING_001_04.log
    sleep 5
    echo "Koncim konverzi do Metadb"
    echo "Koncim konverzi do Metadb" >> LEAF-JPN_VC_NCAP-NVH_BENDING_001_04.log
fi
