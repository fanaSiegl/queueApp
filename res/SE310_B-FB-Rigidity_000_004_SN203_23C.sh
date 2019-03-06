#!/bin/bash
#$ -hard -l qxt2=135
#$ -q abaqus2@*
#$ -soft -q abaqus2@mb-so2.cax.lan
#$ -cwd 
#$ -j y
#$ -N SE310_B-FB-Rigidity_000_004_SN203_23C
#$ -p -50
#$ -v ver_solver=abaqus2017x
#$ -v sub_allfiles=0
#$ -v ret_allfiles=0
#$ -ac verze=abaqus2017x
#$ -ac popis_ulohy=-
#$ -M stepan.kapounek@idiada.cz
#$ -m bes
umask 0002
scratch_dir=/scr1/scratch/grid/kapounek/$JOB_NAME.$JOB_ID
cd $scratch_dir

echo "Startuji Abaqus"
abaqus2017x job=SE310_B-FB-Rigidity_000_004_SN203_23C scratch=/scr1/tmp cpus=12  

echo "Koncim Abaqus"
/bin/uname -a
# now sleep until lock file disappears
sleep 30 && while [ -f SE310_B-FB-Rigidity_000_004_SN203_23C.lck ]; do sleep 5; done

if [ -r META_queue_session.ses -a -f /usr1/applications/ansa/BETA_CAE_Systems/meta_post_v18.1.1/meta_post64.sh ]; then   #konverze do metadb
    echo "Startuji konverzi do Metadb"
    echo "Startuji konverzi do Metadb" >> SE310_B-FB-Rigidity_000_004_SN203_23C.log
    /usr1/applications/ansa/BETA_CAE_Systems/meta_post_v18.1.1/meta_post64.sh -b -foregr -virtualx_64bit -s META_queue_session.ses SE310_B-FB-Rigidity_000_004_SN203_23C &>> SE310_B-FB-Rigidity_000_004_SN203_23C.log
    sleep 5
    echo "Koncim konverzi do Metadb"
    echo "Koncim konverzi do Metadb" >> SE310_B-FB-Rigidity_000_004_SN203_23C.log
fi

