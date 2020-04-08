#ANSA_GENERAL_COMMENT;~
#$ Project:     SK316_5CS~
#$ Description: Rear bumper~
#$ Responsible: Jan Stekly, jan.stekly@idiada.com, Applus IDIADA Group~
#$~
#$ Modification history:~
#$~
#n SK3165EUB_AIQ_rear_bumper_003_2015~
#i   rear bumper model for pendel test +23C~
#d   6.12.2018~
#a   Lukas Kadlec, IDIADA CZ~
#c     - source:~
#c       5LG_807_000____GEO_TM__001_____ZIERLEISTE_________B-FREI____2018_11_22~
#c       5LG_807_000____GEO_TMG_000_____AHK_VERSTAERKERUNG_B-FREI____2018_11_26~
#c       5LG_807_393____GEO_TM__003_____FUEHRUNGSPROFIL_LI_PS-24622______181122~
#c       5LG_807_393_A__GEO_TM__003_____FUEHRUNGSP_SBBR_LI_PS-24623______181121~
#c       5LG_807_421____GEO_TM__001_____ABDECKUNG_HINTEN_________________181122~
#c       5LG_807_441____GEO_TM__003_____ABDECKUNG_ABSCHLEP_______________181126~
#c       5LG_807_521_H__GEO_TM__002_000_SPOILER________________________181126__~
#c       5LG_807_568____GEO_TM__001_____DIFUZOR____________B-FREI____2018_11_26~
#c       5LG_807_863____GEO_TM__003_____BEFESTIGUNGSLEISTE_______A_______181126~
#c      - Abdeckung and Befestigunsleiste were updated according to 2018_12_3~
#c      - MID defined according to SKODA AUTO definition for temperature +23C~
#r      - model for pendel test~
#n SK3165EUB_BIQ_rear_bumper_003_2015~
#i   rear bumper model for pendel test +23C~
#d   11.12.2018~
#a   Lukas Kadlec, IDIADA CZ~
#c      - Include was renamed~
#r      - model for pendel test~
#n SK3165EUB_BIU_003_2015~
#i   SK3165EUB_BIU_003~
#d   14.12.2018~
#a   jodas~
#c    <SK3165EUB_BIQ_car_001_2015>~
#c     - Halter STF were modified to avoid intersection with Spoiler~
#c     - renumbered in range~
#c     - Headlamps taken from P-release~
#c     - Unpenetrated with respect to RBU~
#c     - Sets for Pendulum defined~
#r     - car for Pendulum~
#c    <SK3165EUB_AIQ_rear_bumper_003_2015>~
#c     - source:~
#c       5LG_807_000____GEO_TM__001_____ZIERLEISTE_________B-FREI____2018_11_22~
#c       5LG_807_000____GEO_TMG_000_____AHK_VERSTAERKERUNG_B-FREI____2018_11_26~
#c       5LG_807_393____GEO_TM__003_____FUEHRUNGSPROFIL_LI_PS-24622______181122~
#c       5LG_807_393_A__GEO_TM__003_____FUEHRUNGSP_SBBR_LI_PS-24623______181121~
#c       5LG_807_421____GEO_TM__001_____ABDECKUNG_HINTEN_________________181122~
#c       5LG_807_441____GEO_TM__003_____ABDECKUNG_ABSCHLEP_______________181126~
#c       5LG_807_521_H__GEO_TM__002_000_SPOILER________________________181126__~
#c       5LG_807_568____GEO_TM__001_____DIFUZOR____________B-FREI____2018_11_26~
#c       5LG_807_863____GEO_TM__003_____BEFESTIGUNGSLEISTE_______A_______181126~
#c      - Abdeckung and Befestigunsleiste were updated according to 2018_12_3~
#c      - MID defined according to SKODA AUTO definition for temperature +23C~
#r      - model for pendel test~
#c    <SK3165EUB_BIQ_rear_bumper_003_2015>~
#c      - Include was renamed~
#r      - model for pendel test~
#c    <SK3165EUB_AIB_rear_defo_012_2015>~
#c     - source CAD:~
#c     11A_807_305_DMU_EN__001_TRAEGER_STOSSF_HI__RICHTUNG_B-FR_181011.CATPart~
#c     - CMS based on CAD data~
#c     - Depenetrated with car~
#r     - New development state~
#c    <SK3165EUB_AIB_rear_defo_018_2015>~
#c     - source CAD:~
#c     ZWA_SK316_-_ZADNI_VYZTUHA-1.CATPart~
#c     - Upgrade SQTR+Schottplatte according CAD 24.10.2018~
#c     - Depenetrated with car~
#r     - New development state~
#c    <SK3165EUB_AIB_rear_defo_022_2015>~
#c     - Changed mater of defo from HX420LAD to DP780~
#r     - New development state~
#c    <SK3165EUB_AIB_rear_defo_024_2015>~
#c     - Changed thickness of defo from 1,7/2,2mm->1,7/1,7mm~
#r     - New development state~
#c    <SK3165EUB_AIB_rear_defo_025_2015>~
#c     - Changed thickness of defo 1,9/1,9mm~
#r     - New development state~
#c    <SK3165EUB_AIB_rear_defo_026_2015>~
#c     - Changed thickness of defo 1,8/1,8mm~
#r     - New development state~
#c    <SK3165EUB_AIB_rear_defo_029_2015>~
#c     - Added welds to Inner and Outer side of defo~
#r     - New development state~
#c    <SK3165EUB_AIB_rear_defo_031_2015>~
#c     - Modified welds~
#r     - New development state~
#c    <SK3165EUB_AIB_rear_defo_032_2015>~
#c     - Modified welds II.~
#r     - New development state~
#c    <SK3165EUB_BIB_rear_defo_033_2015>~
#c     - Depenetrated foam~
#c     - Add group: RDE_CNTAC_10_FGS_foam~
#c     - Add group: RDE_TIED_S_FGS_foam_connection~
#c     - Add group: RDE_TIED_M_FGS_foam_connection~
#c     - Add group: tied_abschleppoese_master~
#c     - Add group: RDE_RBODY_mounting_global~
#c     - Add CNTACs: RDE_FGS_foam,  RDE_FGS_foam_connection~
#r     - Renamed include by pendulum convetion~
###############################################################################~
#;
#
#
#
INCLU / ./test_level/SK3165EUB_BIQ_car_001_2015.inc
INCLU / ./test_level/SK3165EUB_BIQ_rear_bumper_003_2015.inc
INCLU / ./test_level/SK3165EUB_BIB_rear_defo_033_2015.inc
