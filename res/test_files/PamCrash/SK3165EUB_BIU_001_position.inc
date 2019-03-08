#ANSA_GENERAL_COMMENT;~
#$ Project:     SK3165EUB~
#$ Description: Material test - Rear Bumper~
#$ Responsible: Miroslav Soukup, miroslav.soukup@skoda-auto.cz, EKF~
#$~
#$ Modification history:~
#$~
#n SK3165EUB_BIU_001_position~
#i   Position for EHK42 angle 0 degrees, z=50.57mm, vehicle mass 2152 kg~
#d   12.12.2018~
#a   Lukas Kadlec, IDIADA CZ~
#l     - impact velocity: 1.1110 m/s = 4 km/h~
#l     - car Leergewicht: xxxx kg~
#l     - car weihgt: xxxx kg (Leergewicht + 3*75kg)-5%~
#l     - pendulum weight: xxxx kg (Leergewicht)~
###############################################################################~
#;
#ANSA_USER_ATTRIBUTES;SK3165EUB_AIQ_002_position.inc;INCLUDE;DM/IO Index;TEXT;4;
#
#
#
# 
# PARAMETERS
# 
PYVAR /        1
NAME
#IMP MASS 2152kg, CAR MASS UNLADEN 2152 kg, LADEN 2377 kg
IMP_MASS = 2137
CAR_MASS = 2122
ROLL_RESIST = 2152 * 9.81 * 0.01
END_PYVAR 
NSMAS /        1<IMP_MASS      >                                                
NAME Additional_weight
#ANSA_ID;6;
        GRP  'IMP_NSMAS_Additional_weight'
        END
#---5---10----5---20----5---30----5---40----5---50----5---60----5---70----5---80
# Prescription of the initial velocity (4.0km/h)
#           NODE   VELX0   VELY0   VELZ0  VANGX0  VANGY0  VANGZ0   IFRAM
INVEL /        01.111111     0.0     0.0     0.0     0.0     0.096000001
NAME Impactor
        GRP 'IMP_INVEL_Impactor'
        END
#---5---10----5---20----5---30----5---40----5---50----5---60----5---70----5---80
TRSFM / 
NAME Impactor_positioning
        GRP 'IMP_TRSFM_Impactor_Positioning'
        END
# Basic positioning - according to the impact point
        MOVE   3665.00              1.0        0.0        0.0        0        0
        MOVE   -110.00              0.0        1.0        0.0        0        0
        MOVE     50.57              0.0        0.0        1.0        0        0
        END
TRSFM / 
NAME Impactor_positioning_rot
        GRP 'IMP_TRSFM_Impactor_Positioning'
        END
# Basic positioning - according to the impact point
$ Translations:          VALUE        TX        TY        TZ     NODE1     NODE2
        ROTA        0 96001316       0.0       0.0        1.0        0        0
        END
