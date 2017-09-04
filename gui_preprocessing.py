#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 15:15:03 2017

preprocessing gui

@author: biahan
"""
#%%
from Tkinter import *
import Tkinter, Tkconstants, tkFileDialog, tkMessageBox

import ttk
import os
from shutil import *
import subprocess

f1=open('./gui_preprocessing_config','r').read()
exec(f1)


master = Tk()
directory = tkFileDialog.askdirectory()
master.destroy()
files = os.listdir(directory)
master = Tk()
var = []
varlist=[]
subjlist=[]
selection_list = dict()

def show_entry_fields():
    for ii in range(len(varlist)):
        selection_list[subjlist[ii]]=varlist[ii].get()
    master.destroy()


for i in range(len(files)):
    if files[i].find("sub")==0:
        var = IntVar()
        Checkbutton(master, text=files[i], variable = var).grid(row=i+1,column=0)
        varlist.append(var)
        subjlist.append(files[i])

Button(master, text='Confirm', command=show_entry_fields).grid(row=i+2, column=1, sticky=W, pady=4)

mainloop()

#%%

f = open(directory+'/../scripts/subjects.txt','w')


for (key,value) in selection_list.items():
    if value==1:
        f.write(key+'\n')
f.close()

#%% preprocessing
master = Tk()

def brain_extraction():
    for (key,value) in selection_list.items():
         if value==1:
            subj_dir = directory+'/'+key+'/'
            anat_dir = subj_dir +'anat/'+key+'_anat.nii.gz '
            anat_brain_dir = subj_dir + 'anat/'+key+'_anat_brain.nii.gz '
            cmdline = "bet "+anat_dir+anat_brain_dir+"-f 0.5 -g 0 -o"
            Label(master, text='waiting for '+ key).grid(row=4,column=1)
            master.update()
            output=subprocess.check_output(cmdline,shell=True)
            Label(master, text='finished: '+ key).grid(row=4,column=1)
            master.update()
            print(output)            
    #master.destroy()

    
def run_freesurfer():
    log_directory = tkFileDialog.askdirectory(title="Select a Log Directory",initialdir=directory+'/../logs/freesurfer' )
    for (key,value) in selection_list.items():
         if value==1:
             subj_dir = directory+'/'+key+'/'
             anat_dir = subj_dir +'anat/'+key+'_anat.nii.gz'
             anat_brain_dir = subj_dir + 'anat/'+key+'_anat_brain.nii.gz'
             if os.path.exists(anat_brain_dir):
                 cmdline = "echo " + "\"recon-all -i "+ anat_brain_dir +" -all -subjid fs -sd "+ subj_dir + " \" " + "> "+log_directory+"/"+key+"_fs.sh"
                 Label(master, text= key + ': wrtie to sh file' ).grid(row=5,column=1)
                 master.update()
                 output=subprocess.check_output(cmdline,shell=True)
                 print(output)  
                 Label(master, text= key + ': begin to submit to cluster' ).grid(row=5,column=1)
                 master.update()               
                 cmdline = "qsub -N \'fs_"+ key + "\' -l \'procs=1,mem=12gb,walltime=22:00:00' "+log_directory+"/"+key+"_fs.sh"
                 output=subprocess.check_output(cmdline,shell=True)
                 print(output)                   
                 Label(master, text= key + ': finished the submission to cluster' ).grid(row=5,column=1)
                 master.update()
             else:
                 tkMessageBox.showerror("error","No extracted brain for "+ key + ", run extraction first")
                
def replace_word(infile,old_word,new_word):
    if not os.path.isfile(infile):
        print ("Error on replace_word, not a regular file: "+infile)
        sys.exit(1)

    f1=open(infile,'r').read()
    f2=open(infile,'w')
    m=f1.replace(old_word,new_word)
    f2.write(m)

def create_GLM():
    for (key,value) in selection_list.items():
         if value==1:                         
             beh = tkFileDialog.askopenfilename(title="Select down-left session 1 for:"+ key,initialdir=directory+'/'+key+'/info/' )
             if beh.find(condi[0])==-1:
                 tkMessageBox.showerror("error","selection not correct!")
                 break
             else:
                 for i in range(sesnum):
                     new_file =directory+'/../logs/feat/'+key+'_s'+str(i+1)+analysisname+'.fsf'
                     if not os.path.exists(new_file):
                         copy2(directory+'/../logs/feat/'+template_filename, new_file)
                     else:
                         results = tkMessageBox.askquestion("Same", "Analysis "+key+'_s'+str(i+1)+analysisname+" fsf file exists, do it again?", icon='warning')
                         if results=='no':
                             break
                         else:
                             copy2(directory+'/../logs/feat/'+template_filename, new_file)                             

                     replace_word(new_file,template_project_dir,directory)
                     replace_word(new_file,"set fmri(outputdir) \""+template_output_dir+"\"","set fmri(outputdir) \""+directory+"/"+key+"/func/"+key+analysisname+'_s'+str(i+1)+"\"")
                     replace_word(new_file,template_4dfile,sesname[i])
                     replace_word(new_file,'sub-1',key)
                     
                     for cond in condi:
                         beh_new=beh.replace(condi[0],cond)
                         beh_ses=beh_new.replace('s1','s'+str(i+1))
                         replace_word(new_file,beh_new,beh_ses)
                     if i>0:
                         replace_word(new_file,'set fmri(alternateReference_yn) 0','set fmri(alternateReference_yn) 1')
                         replace_word(new_file,'set fmri(confoundevs) 0', "set fmri(confoundevs) 0\n\n# Session's alternate reference image for analysis 1 \nset alt_ex_func(1) \""+directory+"/"+key+"/func/"+key+analysisname+'_s1.feat/example_func.nii.gz\"')
                                      #not finished
                 Label(master, text='finished: '+ key).grid(row=7,column=1)
                 master.update()

def run_ses_1():
    log_directory = tkFileDialog.askdirectory(title="Select a Log Directory",initialdir=directory+'/../logs/feat' )
    for (key,value) in selection_list.items():
         if value==1:
             i=0
             if os.path.exists(directory+key+'/func/'+key+analysisname+'_s'+str(i+1)+'.feat') or os.path.exists(directory+key+'/func/'+key+analysisname+'_s'+str(i+1)+'.gfeat'):
                 results = tkMessageBox.askquestion("Same", "Analysis"+key+analysisname+" exists, do it again?", icon='warning')
                 if results=='no':
                     break
             fsf_file =directory+'/../logs/feat/'+key+'_s'+str(i+1)+analysisname+'.fsf'
             if not os.path.exists(fsf_file):
                 tkMessageBox.showerror("error","fsf file for "+key+'_s'+str(i+1)+analysisname+' doesn\'t exist')

             cmdline = "echo " + "\"feat "+ fsf_file + "\" > "+log_directory+"/"+key+'_s'+str(i+1)+analysisname+".sh"
             Label(master, text= key + ': wrtie to sh file' ).grid(row=8,column=1)
             master.update()
             output=subprocess.check_output(cmdline,shell=True)
             print(output)  
             Label(master, text= key + ': begin to submit to cluster' ).grid(row=8,column=1)
             master.update()               
             master.update()               
             cmdline = "qsub -N \'feat_"+ key + "\' -l \'procs=1,mem=12gb,walltime=22:00:00' "+log_directory+"/"+key+'_s'+str(i+1)+analysisname+".sh"
             output=subprocess.check_output(cmdline,shell=True)
             print(output)                   
             Label(master, text= key + ': finished the submission to cluster' ).grid(row=8,column=1)
             master.update()

 
def run_ses_else():
    log_directory = tkFileDialog.askdirectory(title="Select a Log Directory",initialdir=directory+'/../logs/feat' )
    for (key,value) in selection_list.items():
         if value==1:
             if not os.path.exists(directory+"/"+key+"/func/"+key+analysisname+'_s1.feat/example_func.nii.gz'):
                 tkMessageBox.showerror("error","example_fun.nii.gz not exist yet, wait ses 1 run")
                 break             
             for i in range(1,sesnum):
                 if os.path.exists(directory+key+'/func/'+key+analysisname+'_s'+str(i+1)+'.feat') or os.path.exists(directory+key+'/func/'+key+analysisname+'_s'+str(i+1)+'.gfeat'):
                     results = tkMessageBox.askquestion("Same", "Analysis"+key+analysisname+" exists, do it again?", icon='warning')
                     if results=='no':
                         break
                 fsf_file =directory+'/../logs/feat/'+key+'_s'+str(i+1)+analysisname+'.fsf'
                 if not os.path.exists(fsf_file):
                     tkMessageBox.showerror("error","fsf file for "+key+'_s'+str(i+1)+analysisname+' doesn\'t exist')
    
                 cmdline = "echo " + "\"feat "+ fsf_file + "\" > "+log_directory+"/"+key+'_s'+str(i+1)+analysisname+".sh"
                 Label(master, text= key + ': wrtie to sh file' ).grid(row=9,column=1)
                 master.update()
                 output=subprocess.check_output(cmdline,shell=True)
                 print(output)  
                 Label(master, text= key + ': begin to submit to cluster' ).grid(row=9,column=1)
                 master.update()               
                 master.update()               
                 cmdline = "qsub -N \'feat_"+ key + "\' -l \'procs=1,mem=12gb,walltime=22:00:00' "+log_directory+"/"+key+'_s'+str(i+1)+analysisname+".sh"
                 output=subprocess.check_output(cmdline,shell=True)
                 print(output)                   
                 Label(master, text= key + ': finished the submission to cluster' ).grid(row=9,column=1)
                 master.update()       

from time import gmtime, strftime


def reg_T1():
    for (key,value) in selection_list.items():
         if value==1:
               if not os.path.exists(directory+"/"+key+"/masks"):
                   os.makedirs(directory+"/"+key+"/masks")             
    log_directory = tkFileDialog.askdirectory(title="Select a Log Directory for registeration",initialdir=directory+'/../logs/reg' )
    reg_time = strftime("%Y-%m-%d-%H-%M", gmtime())
    new_file = log_directory +'/''freesurfer2T1'+reg_time+'.sh'
    copy2(directory+'/../scripts/preprocessing/localizer/register_freesurfer_V1_to_T1.sh',new_file)
    replace_word(new_file,"/project/3018012.17/${PROJECT}",directory+'/..')
    Label(master, text= 'wrtie to sh file' ).grid(row=11,column=1)
    master.update()
    cmdline='chmod 777 '+new_file
    output=subprocess.check_output(cmdline,shell=True)    
    print(output)        
    cmdline = 'bash '+new_file    
    output=subprocess.check_output(cmdline,shell=True)
    print(output)  
    Label(master, text= 'finished' ).grid(row=11,column=1)
    master.update()


def reg_func():
    for (key,value) in selection_list.items():
         if value==1:
             for i in range(sesnum):
                 if not os.path.exists(directory+"/"+key+"/func/"+key+analysisname+'_s'+str(i+1)+'.feat'):
                    tkMessageBox.showerror("error","feat "+key+analysisname+'_s'+str(i+1)+"not complete!")
                    break
                 cmdline='flirt -in ${subj_id}_V1.nii.gz -applyxfm -init ../func/localizer_hp128_fwhm5.feat/reg/highres2example_func.mat -out ${subj_id}_V1_example_func.nii.gz -paddingsize 0.0 -interp nearestneighbour -ref ../func/localizer_hp128_fwhm5.feat/reg/example_func.nii.gz'
                 cmdline=cmdline.replace('${subj_id}',directory+"/"+key+'/masks/'+key)
                 cmdline=cmdline.replace('../func/localizer_hp128_fwhm5',directory+"/"+key+"/func/"+key+analysisname+'_s'+str(i+1))
                 Label(master, text= key + ': begin to do V1' ).grid(row=12,column=1)
                 master.update()               
                 output=subprocess.check_output(cmdline,shell=True)
                 print(output)  
                 cmdline=cmdline.replace("_V1","_V2")
                 Label(master, text= key + ': begin to do V2' ).grid(row=12,column=1)
                 master.update()               
                 output=subprocess.check_output(cmdline,shell=True)
                 print(output)  
                 Label(master, text= key + ': finished' ).grid(row=12,column=1)
                 master.update()  
                 
       
    



Label(master, text='Selected sub:'+', '.join({key for (key,value) in selection_list.items() if value==1})).grid(row=0,column=0)

ttk.Separator(master,orient = HORIZONTAL).grid(row=1,column=0,sticky="ew")

Label(master, text='What do you want to do?').grid(row=2,column=0)
ttk.Separator(master,orient = HORIZONTAL).grid(row=3,column=0,sticky="ew")
Button(master, text='brain extraction (BET)', command=brain_extraction).grid(row=4, column=0, sticky=W, pady=0)
Button(master, text='Freesurfer (on cluster)', command=run_freesurfer).grid(row=5, column=0, sticky=W, pady=0)
ttk.Separator(master,orient = HORIZONTAL).grid(row=6,column=0,sticky="ew")
Button(master, text='Create GLM file', command=create_GLM).grid(row=7, column=0, sticky=W, pady=0)
Button(master, text='Run Sesion 1 (on cluster)', command=run_ses_1).grid(row=8, column=0, sticky=W, pady=0)
Button(master, text='Run Other Sesions ', command=run_ses_else).grid(row=9, column=0, sticky=W, pady=0)
ttk.Separator(master,orient = HORIZONTAL).grid(row=10,column=0,sticky="ew")
Button(master, text='V1 and V2 ==> T1', command=reg_T1).grid(row=11, column=0, sticky=W, pady=0)
Button(master, text='V1 and V2 ==> function', command=reg_func).grid(row=12, column=0, sticky=W, pady=0)


#ttk.Separator(master,orient = HORIZONTAL).grid(row=6,column=0,sticky="ew")
mainloop()



