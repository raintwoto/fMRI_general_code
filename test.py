#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  6 00:36:10 2017

@author: biahan
"""


alter_content='''
# Session's alternate reference image for analysis 1 
set alt_ex_func(1) "DIRECTORY-X/SUB-X/func/SUB-X_task_hp128_fwhm0_s1.feat/example_func.nii.gz"
'''
    
EV_content1 = '''
# EV NUM_X title
set fmri(evtitleNUM_X) "EV_NAMEX"

# Basic waveform shape (EV NUM_X)
# 0 : Square
# 1 : Sinusoid
# 2 : Custom (1 entry per volume)
# 3 : Custom (3 column format)
# 4 : Interaction
# 10 : Empty (all zeros)
set fmri(shapeNUM_X) 3

# Convolution (EV NUM_X)
# 0 : None
# 1 : Gaussian
# 2 : Gamma
# 3 : Double-Gamma HRF
# 4 : Gamma basis functions
# 5 : Sine basis functions
# 6 : FIR basis functions
set fmri(convolveNUM_X) 3

# Convolve phase (EV NUM_X)
set fmri(convolve_phaseNUM_X) 0

# Apply temporal filtering (EV NUM_X)
set fmri(tempfilt_ynNUM_X) 1

# Add temporal derivative (EV NUM_X)
set fmri(deriv_ynNUM_X) 1

# Custom EV file (EV NUM_X)
set fmri(customNUM_X) "DIRECTORY-X/SUB-X/info/SUB-X_sSESSIONX_EV_NAMEX.txt"
'''
EV_content2 = '''
# Orthogonalise EV NUM_X wrt EV NUM_Y
set fmri(orthoNUM_X.NUM_Y) 0

'''

       
def EV_replace_value(directory,SUB_X,SESSIONX):
    header=open('./header','r').read()
    footer=open('./footer','r').read()
    al     = alter_content[:]
    EV1    = EV_content1[:]
    EV2    = EV_content2[:]
    header = header.replace('DIRECTORY-X',directory)
    footer = footer.replace('DIRECTORY-X',directory)
    al = al.replace('DIRECTORY-X',directory)
    EV1 = EV1.replace('DIRECTORY-X',directory)
    EV2 = EV2.replace('DIRECTORY-X',directory)
    
    header =  header.replace('SESSIONX',SESSIONX)
    footer = footer.replace('SESSIONX',SESSIONX)
    al = al.replace('SESSIONX',SESSIONX)
    EV1 = EV1.replace('SESSIONX',SESSIONX)
    EV2 = EV2.replace('SESSIONX',SESSIONX)
    
    header = header.replace('SUB-X',SUB_X)
    footer = footer.replace('SUB-X',SUB_X)
    al = al.replace('SUB-X',SUB_X)
    EV1 = EV1.replace('SUB-X',SUB_X)
    EV2 = EV2.replace('SUB-X',SUB_X)
    
    return EV1,EV2,header,footer,al

# EV1,EV2,header,footer,al = EV_replace_value('aa','bb','1')
# for EV_sess in ['a','b','c','d']:
#     EV1,EV2,header,footer,al = EV_replace_value(EV_sess,'bb2','3')
#     print header
#     EV1,EV2,header,footer,al = EV_replace_value(EV_sess,'bb22','3')
#     print header


EV_sessions=['1','2','3']
directory = './'
EV_subject = 'sub-3'
EV_condis = ['a','250v','vv']
EV_alter = 0
EV_alter2=0
analysisname = 'qq'
for EV_sess in EV_sessions:
             EV1,EV2,header,footer,al = EV_replace_value(directory,EV_subject,EV_sess)
             EV_conds =''
             fsf_full = ''
             for i in range(0,len(EV_condis)):
                 EV_cond = EV1.replace('EV_NAMEX',EV_condis[i])
                 EV_cond = EV_cond.replace('NUM_X',str(i+1))                 
                 
                 for j in range(0,len(EV_condis)+1):
                     EV_2 = EV2
                     EV_2 = EV_2.replace('NUM_X',str(i+1)) 
                     EV_2 = EV_2.replace('NUM_Y',str(j)) 
                     EV_cond = EV_cond +EV_2
                 EV_conds = EV_conds + EV_cond
             if EV_alter:
                fsf_full = header + al
             else:
                 if EV_alter2:
                     if EV_sess == '1':
                         fsf_full = header
                     else:
                         fsl_full = header + al
                 else:
                     fsf_full = header
                    
             fsf_full = fsf_full + EV_conds
             fsf_full = fsf_full + footer
               
             new_file =directory+'./gui/'+EV_subject+'_s'+EV_sess+analysisname+'.fsf'
             text_file = open(new_file, "w")
             text_file.write(fsf_full)
             text_file.close()