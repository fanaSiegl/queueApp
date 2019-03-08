#ANSA_GENERAL_COMMENT;~
#$ Project:           xxx~
#$ Description:       ECE R-42~
#$ Responsible:       M. Soukup, miroslav.soukup@skoda-auto.cz, Skoda TK/4~
#$~
#$ Modification history:~
#$~
#n impactor_xIT_001_~
#i   Impactor for homologation test~
#d   8.12.2010~
#a   Andrea Runaninova, TK/44~
#c     - source: pendelimpaktor_se250_r4_vo_r42_c_sop_a_001.inc~
#c     - added: GROUPs, BOUNC, FRAME~
#c     - renumbered from 9600001 to from 9600001~
#r     - model of impactor for homologation test~
#n SKxxx_xIT_impactor_002_2008~
#i   Impactor for homologation test~
#d   16.08.2011~
#a   Jan Stekly, Idiada~
#c     - renumbered by VW~
#c     - defined THNOD on impactor COG name Impactor_COG~
#c     - modify numbers of nodes - 96000001, 96000002~
#r     - unification with IP impactor~
#n SKxxx_xIT_impactor_003_2008~
#i   Impactor for homologation test~
#d   10.01.2012~
#a   Jan Stekly, Idiada~
#c     - modify boundary condition~
#r     - correct impactor~
#n SKxxx_xIT_impactor_101_2008~
#i   Impactor for homologation test, ECE R-42 test~
#d   17.IV.2012~
#a   Jiri Machacek, Swell spol. s r.o.~
#c     - source: pendelimpaktor_hi______________________________se250_ipfb.inc~
#c     - impactor for homologation test, ECE R-42 test~
#c     - impactor in base position 0, 0, 0, rotation 0deg~
#r     - build impactor~
#n SKxxx_xIT_impactor_102_2008~
#i   add pendulum impaktor material to the include, ECE R-42 test~
#d   02.08.2016~
#a   Jiri Machacek, Swell spol. s r.o.~
#c     - add pendulum impaktor material to the include~
#c     - add material MID 8112300, null steel material from~
#c       SKxxx_xAB_materials_023_2008.inc~
#c     - renamed added materila from MID 8112300 to 96000001~
#c     - change material in impactor part~
#r     - compatibility with gpc script~
#n SKxxx_xIU_impactor_103_2008~
#i   change IFRATY option from 0 to 1 in impaktor coordination frame~
#d   01.11.2017~
#a   Jiri Machacek, Swell spol. s r.o.~
#c     - change IFRATY option from 0 to 1 in impaktor coordination frame~
#c     - change IFRATY option from 0 to 1 in frame ID 96000001~
#c     - IFRATY 1 orientation is fixed during the entire run~
#r     - impactor is free only x-axes LOC~
###############################################################################~
#;
#
#
#
#---5---10----5---20----5---30----5---40----5---50----5---60----5---70----5---80
#ANSA_FROZEN_ID;96000001;NODE;YES;
#ANSA_FROZEN_DELETE;96000001;NODE;YES;
#
NODE  / 96000001            153.              0.              0.
#ANSA_FROZEN_ID;96000002;NODE;YES;
#ANSA_FROZEN_DELETE;96000002;NODE;YES;
#
