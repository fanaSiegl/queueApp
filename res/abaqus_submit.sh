#!/bin/bash
#inicializace promennych
#maxcpu=11
maxcpu=24
sub_allfiles=0
ret_allfiles=0
job_perturbation=0
cmd_par=""
lic_token=2 #1=flexnet/2=dsls
exec_host="mb-so2.cax.lan"  #default execution host
USERNAME=${USER%@*}  #orizneme vse za @ - odstranit cax.lan

#zpracovani paramertu
if ! [ -z "$1" ]; then
  if [ "$1" == "datacheck" ]; then 
    cmd_par="datacheck" 
    cmd_par_datacheck=1
    echo "Is selected only datacheck..."
  fi
fi

#Zacatek deklarace funkci ######################################################################

function f_inp_file () {
#### vyber vstupniho souboru *inp z aktualniho adresare
#dame uzivateli vybrat variantu ulohy
local _files
local _file
local _job_num
_files=`ls -1 *.inp 2>/dev/null`

if [ -z "$_files" ]; then
    echo "Error: source file wasn't found *.inp"
    exit 1
fi

echo
ls -1 *.inp | rev | cut -f2 -d"." | rev | grep "" -n | sed "s/:/. /g"
echo
read -p "Enter job number: " _job_num

_file=`ls -1 *.inp | sed -n "${_job_num}p"`

if [ $? -ne 0 ] || [ -z "$_file" ]; then
    echo "Entered job number isn't valid!"
    exit 1
fi

#Navrat nazvu vybraneho souboru xxx.inp
f_inp_file_ret=$_file
}

function f_prepocet_lic () {
#f_prepocet_lic 1
# argument pocet cpu (prepocet cpu)
xx=$1
#Prepocet pocet CPU-> Pocet Flexnet / DSLS 
prepocet_cpu=(  '1' '2'  '3'  '4'  '5'  '6'  '7'   '8'   '9'   '10'  '11'  '12'  '13'  '14'  '15'  '16'  '17'  '18'  '19'  '20'  '21'  '22'  '23'  '24'  '25'\
		'26'  '27'  '28'  '29'  '30'  '31'  '32'  '33'  '34'  '35'  '36'  '37'  '38'  '39'  '40' )
prepocet_flex=( '5' '6'  '7'  '8'  '9'  '10' '11'  '12'  '12'  '13'  '13'  '14'  '14'  '15'  '15'  '16'  '16'  '16'  '17'  '17'  '18'  '18'  '18'  '19'  '19'\
		'19'  '20'  '20'  '20'  '21'  '21'  '21'  '21'  '22'  '22'  '22'  '22'  '23'  '23'  '23' )
prepocet_dsls=( '5' '59' '68' '76' '85' '94' '103' '111' '120' '125' '130' '135' '140' '144' '149' '153' '157' '160' '165' '168' '172' '175' '179' '182' '185'\
		'188' '192' '195' '198' '200' '203' '206' '209' '212' '214' '217' '220' '222' '225' '227' )

#$1 obsahuje pocet CPU ( pole zacina ale od 0 ,proto odecist xx=$xx-1
let "xx--"
if [ $lic_token -eq 1 ]; then 
    # return flexlm pocet lic
    f_prepocet_lic_ret=${prepocet_flex[$xx]}
else
    # return dsls pocet lic
    f_prepocet_lic_ret=${prepocet_dsls[$xx]}
fi
}

#Konec deklarace funkci #######################################################################

#f_prepocet_lic 40
#echo ${f_prepocet_lic_ret}
#exit 1


#### vyber vstupniho souboru *inp z aktualniho adresare
#dame uzivateli vybrat variantu ulohy
f_inp_file
file=$f_inp_file_ret
jobname=`echo $file | sed s/.inp//`

#vybereme zajimave radky ze vstupniho inp souboru a vlozime do pole
#bIFS=$IFS
#IFS=$'\n'
#farray=(`grep -i -e "*INCLUDE, INPUT=" -e " FILE="  -e "^*RESTART, READ" -e "^*RESTART, WRITE" $file `)
#IFS=$bIFS
#echo ${farray[@]}
#for (( i=0 ; i < ${#farray[@]} ; i++ ))
#do
#    echo $a  ${farray[$i]}
#    done

#Zkontrolujeme includy
inc_files=`grep "*INCLUDE, INPUT=" $file | sed "s/\*INCLUDE, INPUT=// ; s/\.\/// ; s/\r//"`
#Zkontrolujeme pripadne results files *fil
fil_files=`grep " FILE=" $file | sed "s/.* FILE=// ; s/,.*/\.fil/"`
#Zkontrolujeme zda je pozadovano predani vsech souboru na solver (data obsahuji *RESTART, READ)
if ( `grep -i -q "^*RESTART, READ" $file ` ); then
    # 
    sub_allfiles=1
    echo ".....Info- Found Abaqus keyword: *RESTART, READ in the file $file"
    #je treba vlozit oldjob
    echo "Enter OldJob for RESTART."
    f_inp_file
    jobname_old=`echo $f_inp_file_ret | sed s/.inp//`
fi

#Zkontrolujeme zda je pozadovano vraceni vsech souboru ze solveru (data obsahuji *RESTART, WRITE)
if ( `grep -i -q "^*RESTART, WRITE" $file ` ); then
    # 
    ret_allfiles=1
    echo ".....Info- Found Abaqus keyword: *RESTART, WRITE in the file $file"
fi

for inc_file in $inc_files ; do
    if ! [ -f $inc_file ]; then
	echo "Error: Missing included file $inc_file!"
	exit 1
    fi
done

for inc_file in $fil_files ; do
    if ! [ -f $inc_file ]; then
	echo "Error: Missing included results file $inc_file!"
	exit 1
    fi
done

#Zkontrolujene zda se jedna o linearni ulohu typu PERTURBATION
#potom je mozne vyuzit s 8 tokeny 8 cpu (abaqus + standard)
#*STEP, .... PERTURBATION
if ( `grep -i -q -e "^\*STEP,.*PERTURBATION" $file ` ); then
    #
    # let "maxcpu=$maxcpu + 1"   #increment nastaven pozdeji
    job_perturbation=1
    echo ".....Info- Found Abaqus keyword: *STEP, ... PERTURBATION in file $file"
    #echo "     MaxCPU is inreased to $maxcpu"
    echo "     MaxCPU is inreased (maxcpu +1)"
fi


#vybrat frontu Abaqus - abaqus1 ,abaqus2, abaqus3 (abaqus-ge)
# nazev fronty urcuje licencni server 
#napr ver_fronta=abaqus1 a id_fronta=1 
# pokud se vybere napr abaqus1 potom i licence se musi jmenovat abaqus1
# pokud je id_fronta "" jedna se defaultni abaqus1 frontu
# prvni hodnota pole je defaultni hodnota
ver_solverlist=( 'abaqus1' 'abaqus1' 'abaqus2' 'abaqus3' )
ELEMENTS=${#ver_solverlist[@]}
echo -e "\n\t---Choose the queue (license server)---"
for (( i=1;i<$ELEMENTS;i++)); do
    ia=${ver_solverlist[${i}]} #obsahuje retezec napr abaqus1
    case "$ia" in
	abaqus1) echo -e $i"->"$ia "\t-COMMERCIAL license (mainly for mb-so3, max. 210 DSLS tokens, free tokens:N/A  )"
	    ;;
	abaqus2) echo -e $i"->"$ia "\t-VAR 2 license (mainly for mb-so2, max. 150 DSLS tokens, free tokens:N/A  )"
	    ;;
	abaqus3) echo -e $i"->"$ia "\t-VAR 1 license (max. 150 DSLS tokens, free tokens:N/A  )"
	    ;;
	*)  echo $i"->"${ver_solverlist[${i}]}
	    ;;
    esac
done
read -p "Enter the number which represent Abaqus queue: [enter=${ver_solverlist[0]}] " sol_num

if [ -z "$sol_num" ]; then
    #id_fronta=""
    ver_fronta=${ver_solverlist[0]}
else
    if [ $sol_num -lt $ELEMENTS ]; then
        ver_fronta=${ver_solverlist[${sol_num}]}
    else
        echo "Entered number is invalid"
        exit 1
    fi
fi
#abaqus1-> id="1", abaqus2-> id="2" apodobne
id_fronta=${ver_fronta#abaqus}
echo -e "\t\t selected is queue: $ver_fronta"

#od 31.1.2018 licence pro frontu abaqus1 jsou dlsl1:dlsl2:dlsl3
#if [ $id_fronta -eq 1 ]; then lic_token=1; fi #pouze fronta abaqus1 pouziva flexnet lic
# echo ${ver_fronta}
# echo ${id_fronta}

#vybrat verzi solveru (abaqus-ge)
#prvni hodnota pole je defaultni hodnota
ver_solverlist=( 'abaqus2017x' 'abaqus6141' 'abaqus2016x' 'abaqus2017x' 'abaqus2018x' 'abaqus2018-HF4' )
ELEMENTS=${#ver_solverlist[@]}
echo -e "\n\t---Choose the Abaqus solver version---"
for (( i=1;i<$ELEMENTS;i++)); do
    echo $i"->"${ver_solverlist[${i}]}
done
read -p "Enter number which represent version of solver[enter=${ver_solverlist[0]}] " sol_num

if [ -z "$sol_num" ]; then
    ver_solver=${ver_solverlist[0]}
    else
    if [ $sol_num -lt $ELEMENTS ]; then
        ver_solver=${ver_solverlist[${sol_num}]}
    else
        echo "Entered number is not valid"
        exit 1
    fi
fi
echo -e "\t\t selected is version: $ver_solver"
# echo $ver_solver

#vyber solveru pro vypocet ulohy
#qstat -f -q ${ver_fronta}
echo -e "\n\t---Choose the execution host---"
bIFS=$IFS
IFS=$'\n'
#sollist=(`grep -i -e "*INCLUDE, INPUT=" -e " FILE="  -e "^*RESTART, READ" -e "^*RESTART, WRITE" $file `)
sollist=(`qstat -f -q ${ver_fronta} | grep -i -e "abaqus" `)
IFS=$bIFS
#echo ${sollist[@]}
#printf  "%s\t" "${sollist[@]}"
echo "---------------------------------------------------------------------------------"
echo "For this queue are defined next execution hosts:"
echo "---------------------------------------------------------------------------------"
#echo -e "\tqueue_name\t\tqtype\tres/use/tot\tload_avg  arch    states"
echo "queuename                      qtype resv/used/tot. load_avg    arch       states"
echo "---------------------------------------------------------------------------------"
for (( i=0 ; i < ${#sollist[@]} ; i++ ))
do
    ic=$((i+1))   #aby se zobrazovalo pocitani od 1 prestoze pole zacina od 0
#    echo $ic"->"  ${sollist[$i]}
    printf "%s\t\n" $ic"->""${sollist[$i]}"
done
echo -e "\t.....Info- your computer is:" `hostname`
echo -e "\t..server mb-so3 (32 cores, 2 GPU, best performance, free cores:N/A)"
echo -e "\t..server mb-so2 (12 cores, 1 GPU, middle performance, free cores:N/A)"
echo -e "\t..server mb-so1 (12 cores, 1 GPU, low performance, free cores:N/A)"
echo -e "\t..workstations (3 cores)"

read -p "Enter the number which represent prefered execution host [enter=mb-so2.cax.lan]: " exec_hostid
if [ -z "$exec_hostid" ] ; then
#jeste doplnit test na nesmyslnou hodnotu vstupu  $exec_hostid -lt ${#sollist[@]} 
    exec_host="${ver_fronta}@mb-so2.cax.lan"
else
    ic=$((exec_hostid-1))   #zobrazovalo se pocitani od 1 ale pole zacina od 0
    #exec_host=`echo ${sollist[$exec_hostid]}| awk '{print $1}'`
    exec_host=`echo ${sollist[$ic]}| awk '{print $1}'`
fi
#echo "sollist:"${#sollist[@]}
echo -e "\t\t selected is prefered execution host: "$exec_host

#Popis ulohy ve fronte - promenna popis_ulohy
read -p "Enter description of job [15 characters, enter=none]: " popis_ulohy
if [ -z "$popis_ulohy" ]; then
    popis_ulohy="-"
else
    popis_ulohy=${popis_ulohy:0:15}
fi

#Nabidneme jiny cas spusteni
ge_time=
read -p "Enter deferred time of cumputation [enter=put ASAP into queue]: " start_time
if [ -n "$start_time" ]; then
    form_time=`date -d "$start_time" 2> /dev/null`
    if [ $? -ne 0 ]; then
        echo "Entered time is invalid!"
        exit 1
    fi
    echo "Time of computation: " $form_time
    ge_time=`date -d "$start_time" +%m%d%H%M`
fi


#Pocet procesoru ??
#Nejprve se nastavi $maxcpu podle solveru
# ${exec_host#*@}  abaqus1@mb-so1.cax.lan vraci hodnotu mb-so1.cax.lan
echo -e "\n\t---Choose the number of CPU---"
case "${exec_host#*@}" in
"mb-so1.cax.lan")
    maxcpu=12
    maxcpu_input=12	#pocet ktery muze uzivatel pozadovat
    maxgpu=1
    ;;
"mb-so2.cax.lan")
    maxcpu=12
    maxcpu_input=12	#pocet ktery muze uzivatel pozadovat
    maxgpu=1
    ;;
"mb-so3.cax.lan")
    maxcpu=32
    maxcpu_input=32	#pocet ktery muze uzivatel pozadovat
    maxgpu=2
    ;;
*)
    maxcpu=3
    maxcpu_input=4	#pocet ktery muze uzivatel pozadovat
    maxgpu=0
    ;;
esac
if [ $job_perturbation -ge "1" ]; then
    let "maxcpu=$maxcpu + 1"
fi

read -p "Enter number of CPU cores [max $maxcpu_input, enter=$maxcpu]: " ncpus
if [ -z "$ncpus" ]; then
    #ncpus=4
    ncpus=$maxcpu
fi
if [ $? -ne 0 ] || [ $ncpus -gt $maxcpu_input ]; then
    echo "Entered number of CPU is invalid!"
    exit 1
fi
echo -e "\t\t selected is number of CPU: "$ncpus


#FLEXLM(lic_token=1)- Standard versus explicit, licence
if [ $lic_token -eq 1 ]; then 
#Spocitame pocet potrebnych licenci
if [ $job_perturbation -ge "1" ]; then
    #job_perturbation uloha,takze staci stejny pocet tokenu jako jader CPU
    let "licenses=0 + $ncpus"
else
    let "licenses=4 + $ncpus"
fi
explicit=`grep "*DYNAMIC, EXPLICIT" $file`
if [ -n "$explicit" -o  $maxgpu -gt 0 ]; then	#pokud neni explicit nebo maxgpu > 0
    features="abaqus${id_fronta}=$licenses,explicit${id_fronta}=$licenses"
    echo -e "\t\t ..GPGPU acceleration is NOT AVAILABLE"
else
    #Pouzit GPGPU (Tesla GPU) podporovano pouze pouze pro implicit ulohy
    #Pri pouziti GPGPU se snizuje pocet $ncpus o hodnotu 1 
    #read -p "Do you want to use NVIDIA GPU acceleration ? [Y/N, enter=N]: " gpgpu
    #if [ -n "$gpgpu" ] && [ "$gpgpu" = "Y" -o "$gpgpu" = "y" ] ; then
    read -p "Enter number of NVIDIA GPU acceleration  [max $maxgpu, enter=0]: " gpgpu
    if [ "$gpgpu" = "" -o "$gpgpu" = "0" ] || [ "$gpgpu" != "1" -a "$gpgpu" != "2" ] ; then
        gpgpu=""
	echo -e "\t\t ..GPGPU acceleration is NOT SELECTED"
    else
        #gpgpu=",gpgpu=1"
        # gpgpu=",gpgpu${id_fronta}=1"
        if [ "$ncpus" -eq "$maxcpu" ] ; then let "ncpus=$ncpus -1" ; fi
	echo -e "\t\t ..selected is GPGPU acceleration: "$gpgpu
    fi
    features="abaqus${id_fronta}=$licenses,standard${id_fronta}=$licenses$gpgpu"
fi
fi

#DSLS(lic_token=2)- QXT licence 
if [ $lic_token -eq 2 ]; then
    #Spocitame pocet potrebnych DSLS licenci
    #    let "licenses=0 + $ncpus"
    #prepocet DSLS tokeny na CPU cores (zatim x10)
    #let "licensesdsls=$licenses * 10"
    f_prepocet_lic $ncpus
    licensesdsls=${f_prepocet_lic_ret}

    explicit=`grep "*DYNAMIC, EXPLICIT" $file`
if [ -n "$explicit" -o  $maxgpu -eq 0 ]; then	#pokud je explicit nebo maxgpu = 0
    #features="abaqus${id_fronta}=$licenses,explicit${id_fronta}=$licenses"
    features="qxt${id_fronta}=$licensesdsls"
    echo -e "\t\t ..GPGPU acceleration is NOT AVAILABLE (maxGPU=$maxgpu) $explicit"
else
    #Pouzit GPGPU (Tesla GPU) podporovano pouze pouze pro implicit ulohy
    #Pri pouziti GPGPU se snizuje pocet $ncpus licenci o hodnotu 5 
#    read -p "Do you want to use NVIDIA GPU acceleration ? [Y/N, enter=N]: " gpgpu
    read -p "Enter number of NVIDIA GPU acceleration  [max $maxgpu, enter=0]: " gpgpu
    if [ "$gpgpu" = "" -o "$gpgpu" = "0" ] || [ "$gpgpu" != "1" -a "$gpgpu" != "2" ] ; then
        gpgpu=""
	echo -e "\t\t ..GPGPU acceleration is NOT SELECTED"
    else
	#gpgpu=",gpgpu${id_fronta}=1"
        if [ "$ncpus" -eq "$maxcpu" ] ; then let "ncpus=$ncpus -5" ; fi
	echo -e "\t\t ..selected is GPGPU acceleration: "$gpgpu
    fi
    #features="abaqus${id_fronta}=$licenses,standard${id_fronta}=$licenses$gpgpu"
    features="qxt${id_fronta}=$licensesdsls"
fi
#features="qxt${id_fronta}=$licensesdsls"
fi

#Nastaveni priority ulohy ve fronte
qpriority=50
read -p "Enter priority in the queue [40-60, enter=50]: " qpriority
if [ -z "$qpriority" ]; then
        if [ "$cmd_par_datacheck" = 1 ]; then
    	    #datacheck uloha ma mit prednost -> priority=65
	    qpriority=65
	else
    	    qpriority=50
        fi
    else
    if [ "$qpriority" -gt 60 ] || [ "$qpriority" -lt 40 ]; then
     qpriority=50
    fi
fi
#prepocet priority do zapornych hodnot ( + hodnoty vyzaduji Operator privelgia)
 qpriority=$(( $qpriority - 100 ))
echo "Priority of job was set to: $qpriority"


#Vytvoreni prikazu na spusteni
#cmd="abaqus-ge job=$jobname"
cmd="$ver_solver job=$jobname scratch=/scr1/tmp"
if [ $sub_allfiles -eq 1 ]; then
    cmd="$cmd oldjob=$jobname_old"
fi

#Pokud pro vice procesoru, pridame potrebne parametry
if [ $ncpus -gt 1 ]; then
    if [ -n "$explicit" ]; then
	#explicit
	#cmd="$cmd parallel=domain cpus=$ncpus mp_mode=mpi domains=$ncpus"
	cmd="$cmd parallel=domain cpus=$ncpus domains=$ncpus"
    else
	#standard
	if [ -n "$gpgpu" ]; then
	    #je pozadovana akcelerace GPGPU (pro abaqus6141 je odlisna syntaxe gpu=nvidia u vyssich verzi gpus=1
	    #vyriznout z promenne $ver_solver=abaqus2017x 6-9.znak
	    #if [ ${ver_solver#abaqus} -le 6111 ] ; then
	    if [ ${ver_solver:6:4} -eq 6141 ] ; then
		cmd="$cmd cpus=$ncpus mp_mode=mpi gpu=nvidia "
	    else
		#cmd="$cmd cpus=$ncpus mp_mode=mpi gpus=1 "
		#cmd="$cmd cpus=$ncpus gpus=1 "
		cmd="$cmd cpus=$ncpus gpus=$gpgpu "
	    fi
	else
	    #cmd="$cmd cpus=$ncpus mp_mode=mpi "
	    cmd="$cmd cpus=$ncpus  "
	fi
    fi
fi

#Dalsi parametry prikazu Abaqus ?
read -p "Here is possible to specify more Abaqus job parameters [15 characters, enter=none]: " abaq_par
if ! [ -z "$abaq_par" ]; then
    cmd_par="$cmd_par ${abaq_par:0:15}"
fi


#Pokud byl pozadovan datacheck,nebo dalsi parametry Abaquas - pridame parametr na konec cmd
if ! [ -z "$cmd_par" ]; then
    cmd="$cmd $cmd_par"    
    echo "---Special parameters: $cmd_par"
fi

#pokud nejou data na serveru nakopirujeme data na server a zmenime adresar
#mounted=`df . | grep "/data/fem"`
mounted=`df . | egrep "/data/fem|/data/sk_1|/data/sk_2|/data/vwg|/data/bmw|/data/fgs|/data/simulia|/data/ostatni|/data/ostatni_2"`
if [ -z "$mounted" ]; then
    #jsme na lokalu

    for (( i=1 ; i<100 ; i++ )); do
	jobdir=/data/fem/grid/$USERNAME/$jobname.$i
    	if ! [ -d $jobdir ]; then
	    mkdir -p $jobdir
	    if [ $? -ne 0 ]; then
		echo "Error: failed to create directory $jobdir!"
		exit 1 
	    fi
	    
	    #Nakopirujeme soubory
	    if [ sub_allfiles=0 ]; then
		allfiles="$file $inc_files $fil_files"
	    else
		#zkopirovat vsechny soubory ulohy
		allfiles="$jobname $inc_files $fil_files"
	    fi
	    for cp_file in $allfiles; do
    		cp $cp_file $jobdir/
		if [ $? -ne 0 ]; then
		    echo "Chyba: failed to copy file $cp_file into folder $jobdir!"
		    exit 1
		fi
	    done

	    cd $jobdir
	    break	
	fi
    done

fi

cat > $jobname.sh << _EOF
#!/bin/bash
###$ -hard -l $features -l excl=true
#$ -hard -l $features 
#$ -q ${ver_fronta}@*
#$ -soft -q ${exec_host}
#$ -cwd 
#$ -j y
#$ -N $jobname
#$ -p $qpriority
#$ -v ver_solver=$ver_solver
#$ -v sub_allfiles=$sub_allfiles
#$ -v ret_allfiles=$ret_allfiles
#$ -ac verze=$ver_solver
#$ -ac popis_ulohy=$popis_ulohy
_EOF
if [ -n "$ge_time" ]; then
    echo "#$ -a $ge_time" >> $jobname.sh
fi
if [ -n "$GE_MAIL" ]; then
    echo "#$ -M $GE_MAIL" >> $jobname.sh
    echo "#$ -m bes" >> $jobname.sh
else
    echo "Variable GE_MAIL is not defined, mailing is turned off."
fi

#Pokud je nastaven $jobname_old pridat jej do definice promennych
if ! [ -z $jobname_old ]; then
    echo "#$ -v jobname_old=$jobname_old" >> $jobname.sh
fi

cat >> $jobname.sh << _EOF
umask 0002
scratch_dir=/scr1/scratch/grid/$USERNAME/\$JOB_NAME.\$JOB_ID
cd \$scratch_dir

echo "Startuji Abaqus"
$cmd

echo "Koncim Abaqus"
/bin/uname -a
# now sleep until lock file disappears
sleep 30 && while [ -f ${jobname}.lck ]; do sleep 5; done

if [ -r META_queue_session.ses -a -f /usr1/applications/ansa/BETA_CAE_Systems/meta_post_v18.1.1/meta_post64.sh ]; then   #konverze do metadb
    echo "Startuji konverzi do Metadb"
    echo "Startuji konverzi do Metadb" >> $jobname.log
    /usr1/applications/ansa/BETA_CAE_Systems/meta_post_v18.1.1/meta_post64.sh -b -foregr -virtualx_64bit -s META_queue_session.ses $jobname &>> $jobname.log
    sleep 5
    echo "Koncim konverzi do Metadb"
    echo "Koncim konverzi do Metadb" >> $jobname.log
fi

_EOF

echo ".....Info- Required licenses for this job are: $features"

#Provedeme submit ulohy
qsub $jobname.sh
