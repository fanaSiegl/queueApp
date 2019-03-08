#ANSA_GENERAL_COMMENT;~
#$ Project:     SK3762CS~
#$ Description: Front bumper reinforcement assembly~
#$ Responsible: Miroslav Soukup, miroslav.soukup@skoda-auto.cz, Skoda TK/4~
#$~
#$ Modification history:~
#$~
#n SKxxx_xIP_composite_mat_001~
#i   ABS_Chrome material~
#d   8.12.2015~
#a   Jiri Machacek, Swell a.s.~
#c     - source: MAT_compo.inc~
#c       based on Lenam include~
#c     - in this include is defined composite material for ABS with Chrome ply~
#c     - composite is defined like 5-ply of ABS, 2-ply Ni, 2-ply and 2-ply Cu~
#c     - material for -10C, +23C and +65C~
#c     - material is defined for thickness 3.21mm, 3.0mm, 2,75mm, 2.5mm, 2.25mm~
#c       2.0mm, 1.8mm, 1.75mm, 1.6mm, 1.5mm~
#r     - prediction of the damage ABS-Chrome componets~
#n SKxxx_xIP_composite_mat_002~
#i   ABS_Chrome material added th. 1.0mm, ~
#d   8.12.2015~
#a   Jiri Machacek, Swell a.s.~
#c     - source: MAT_compo.inc~
#c     - added thickness 1.0mm MID -10C 90110010, +23C 90110023, +65C 90110065~
#c     - added thickness 1.4mm MID -10C 90114010, +23C 90114023, +65C 90114065~
#c     - added thickness 1.5mm MID -10C 90115010, +23C 90115023, +65C 90115065~
#c     - added thickness 1.7mm MID -10C 90117010, +23C 90117023, +65C 90117065~
#c     - added thickness 1.8mm MID -10C 90118010, +23C 90118023, +65C 90118065~
#c     - added thickness 1.9mm MID -10C 90119010, +23C 90119023, +65C 90119065~
#c     - added thickness 2.1mm MID -10C 90121010, +23C 90121023, +65C 90121065~
#c     - added thickness 2.2mm MID -10C 90122010, +23C 90122023, +65C 90122065~
#c     - added thickness 2.3mm MID -10C 90123010, +23C 90123023, +65C 90123065~
#c     - added thickness 2.4mm MID -10C 90124010, +23C 90124023, +65C 90124065~
#c     - added thickness 2.6mm MID -10C 90126010, +23C 90126023, +65C 90126065~
#c     - added thickness 2.7mm MID -10C 90127010, +23C 90127023, +65C 90127065~
#c     - added thickness 2.8mm MID -10C 90128010, +23C 90128023, +65C 90128065~
#r     - prediction of the damage ABS-Chrome componets~
#n SKxxx_xIP_composite_mat_003~
#i   ABS_Chrome material added th. 1.0mm, ~
#d   8.12.2015~
#a   Jiri Machacek, Swell a.s.~
#c     - source: MAT_compo.inc~
#c     - correct material definition PLY ABS in +23C for MID 90110023,~
#c       90114023, 90115023, 90117023, 90118023, 90119023, 90121023, 90122023,~
#c       90123023, 90124023, 90126023, 90127023, 90128023,~
#r     - bag correction~
#c     - added thickness 4.0mm MID -10C 90140010, +23C 90140023, +65C 90140065~
#c     - added thickness 3.7mm MID -10C 90137010, +23C 90137023, +65C 90137065~
#c     - added thickness 3.6mm MID -10C 90136010, +23C 90136023, +65C 90136065~
#c     - added thickness 3.5mm MID -10C 90135010, +23C 90135023, +65C 90136065~
#r     - new thickness material definition~
#n SKxxx_xIP_composite_mat_004~
#i   ABS_Chrome material added th. 1.2mm~
#d   8.12.2015~
#a   Jiri Machacek, Swell a.s.~
#c     - source: MAT_compo.inc~
#c     - added thickness 1.2mm MID -10C 90112010, +23C 90112023, +65C 90112065~
#r     - new thickness material definition~
#n SKxxx_xIP_composite_mat_005~
#i   ABS_Chrome material added th. 3.21mm for -10C a +65C~
#d   06.01.2017~
#a   Jiri Machacek, Swell a.s.~
#c     - ABS_Chrome material added th. 3.21mm for -10C a +65C~
#c     - added thickness 3.21mm MID -10C 90300010, +65C 90300065~
#r     - new thickness material definition~
###############################################################################~
#;
#
#
#
#---5---10----5---20----5---30----5---40----5---50----5---60----5---70----5---80
MATER / 90128010     131           7.E-6       0       0                
                                                              1.        
NAME Cr-Ni-Cu-ABS-Cu-Ni-Cr__th.2_80__-10C
       0.1        0.   11    0                0.01      0.01      0.01  0.833333
  90300023      0.01        0.
  90310023     0.044        0.
  90320023      0.05        0.
  90331010    0.5184        0.
  90341010    0.5184        0.
  90351010    0.5184        0.
  90361010    0.5184        0.
  90371010    0.5184        0.
  90380023      0.05        0.
  90390023     0.044        0.
  90400023      0.01        0.
              0                             0               
    1   12    2   12    3   12    4   12    5   12    6   12    7   12    8   12
    9   12   10   12   11   12                                                  
                                                                                
                                                                                
