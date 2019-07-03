#ANSA_GENERAL_COMMENT;~
#$ Project:     SKxxx~
#$ Description: Pendel test~
#$ Responsible: Miroslav Soukup, miroslav.soukup@skoda-auto.cz, Skoda TK/4~
#$~
#$ Modification history:~
#$~
#n SKxxx_xIP_mat_001_2008~
#i   Plastic materials for pendel tests~
#d   19.VIII.2011~
#a   Jan Stekly, IDIADA~
#s     - Source: SKxxx_xIP_mat_n10C_001_2008.inc~
#s     - Source: SKxxx_xIP_mat_p65C_001_2008.inc~
#c     - merge the material databases for 65C and -10C~
#c     - delete duplicate materials and not usefull materials~
#r     - base materials for IP test~
#n SKxxx_xIP_mat_002_2008~
#i   Add new EPP material 25, 35, 45, 55, 60, 70 g/l for -10C, +23C and +65C~
#d   12.X.2011~
#a   Jiri Machacek, Swell spol. s r.o.~
#c     - change FID from material name EPP50_p65C_fo_SOL_src_skoEPP MID 7758700~
#c       7758751 -> 7758709~
#c     - sort and colect materials with functions~
#c     - add new EPP materials 25g/l, 35g/l, 45g/l, 55g/l, 60g/l and 70g/l for~
#c       -10C, +23C and +65C~
#c     - formal renamed any funkction and material name~
#r     - add new EPP materilas~
#n SKxxx_xIP_mat_003_2008~
#i   Add new materials based on CAMPUS data~
#d   14.XI.2012~
#a   Jiri Machacek, Swell spol. s r.o.~
#c     - add mat PA6_GF30 for -10C MID 7100110, +23C MID 7100130,~
#c       +65C MID 7100150 based on CAMPUS 5.2 data~
#c     - add mat PA6_GF40 for -10C MID 7100210, +23C MID 7100230,~
#c       +65C MID 7100250 based on CAMPUS 5.2 data~
#c     - add mat PP_GF40 for -10C MID 7200130, +23C MID 7200130,~
#c       +65C MID 7200150 based on CAMPUS 5.2 data~
#c     - add mat PC_ABS for -10C MID 7500110, +23C MID 7500130,~
#c       +65C MID 7500150 based on CAMPUS 5.2 data~
#c     - add mat ASA for -10C MID 7500210, +23C MID 7500230, +65C MID 7500250~
#c       based on CAMPUS 5.2 data~
#c     - add mat PC for -10C MID 7500310, +23C MID 7500330, +65C MID 7500350~
#c       based on CAMPUS 5.2 data~
#r     - better material definition~
#n SKxxx_xIP_mat_004_2008~
#i   Correct material PP_T20~
#d   14.8.2013~
#a   Jiri Machacek, Swell spol. s r.o.~
#c     - correct material PP_T20, MID 7001200, 7001400~
#c     - add material PP_T20 for +23C MID 7001200~
#r     - correct material data fro PP_T20~
#n SKxxx_xIP_mat_005_2008~
#i   Correct function name~
#d   18.2.2014~
#a   Jiri Machacek, Swell spol. s r.o.~
#c     - correct function name for material PP_GF40~
#c     - modify function ID 7200131 name from~
#c       MATERIAL_CELSTRAN_PP-GF40-04__PP_GF40_n10C_co_SHE_sra_usr to~
#c       MATERIAL_CELSTRAN_PP-GF40-04__PP_GF40_p23C_co_SHE_sra_usr~
#r     - formal correct function name~
#n SKxxx_xIP_mat_006_2008~
#i   Add material EPP100 for -10C, +65C~
#d   5.2.2015~
#a   Jiri Machacek, Swell spol. s r.o.~
#c     - added two materials based on Audi Materialexport_EPP.xls file~
#c     - add material EPP100 for -10C MID 7756510~
#c     - add material EPP100 for +65C MID 7756550~
#r     - add new material~
#n SKxxx_xIP_mat_007_2008~
#i   New material for EPP30 for -10C~
#d   8.12.2015~
#a   Jiri Machacek, Swell spol. s r.o.~
#c     - New material for EPP30 for -10C~
#c     - add new material for EPP30 for -10C MID 7700110~
#r     - add new material~
#n SKxxx_xIP_mat_008_2008~
#i   Added PMMA Plexiglass 7M material~
#d   20.01.2017~
#a   Jiri Machacek, Swell a.s.~
#c     - Added PMMA Plexiglass 7M material~
#c     - Added PMMA Plexiglass 7M material for -10C, +23C and +56C, m. typ 143~
#c     - for -10C MID 7500410, for +23C MID 7500430, for +65C MID 7500450~
#r     - add new material~
###############################################################################~
#;
#
#
#
#ANSA_COMMENT;7000100;PAM SHELL Material 103;~
#0 Basic properties:~
#p - description:  ~
#p - source:       ~
#p - mass density: ~
#p - ductility:    -~
#p - yield stress: -~
#p - stress limit: -~
#1 Created: ~
#c - ~
#r - ~
#~
#2 Alternative material name:~
#j - Norm name: -~
#j - Commercial name: ~
#~
#3 Original comment:~
#o Testmaterial         ~
#o Quelle:              ~
#o Dichte:              ~
#o Umgebungsbedingungen -10 Grad Celsius~
#o Einheiten:           kg, mm, msec, kN~
#~
#4 Original function comment:~
#f ~
#;
$          IDMAT   MATYP     massdensity    NINT    ISHG  ISTRAT   IFROZ
MATER /  7000100     103          1.2E-6       0       0       0       0
               0       0       0       0       0       0      1.       0
NAME DAPLEN_VB4411_n10C_po_SHE_src_usr                                           
       0.5CURVE          0.463                0.01      0.01      0.01      0.83
   7000101   7000102   7000103   7000104   7000105   7000106         0         0
        0.     1.E-5     1.E-4     0.001      0.01       0.1        0.        0.
        0.        0.        0.        0.          
                            0.        0.        0.        0.        0.        0.
      EPMX        0.
$---+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
$Compression LOADING
FUNCT /  7000101       0      1.   0.687      0.      0.
NAME MATERIAL_DAPLEN_VB4411_n10C_po_SHE_src_usr
                              0.        0.015177
                        0.001556        0.030076
                        0.003922        0.036774
                        0.006467        0.040472
                        0.009633        0.042034
                          0.0127        0.043025
                        0.024728        0.043383
                         0.28619        0.043509
                END
