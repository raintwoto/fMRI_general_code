#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 15:15:03 2017

preprocessing gui

@author: biahan
"""
#%%

from Tkinter import *
import Tkconstants
import tkFileDialog
import tkMessageBox
import re
import ttk
from ttk import Combobox
import os
from shutil import *
import subprocess
import re


f1 = open('./gui_preprocessing_config', 'r').read()
exec(f1)


master = Tk()
directory = tkFileDialog.askdirectory(
    title="Select data Directory", initialdir=initialdir)

files = os.listdir(directory)
log_directory = tkFileDialog.askdirectory(
    title="Select a Log Directory", initialdir=directory+'/../logs/')


if not os.path.exists(log_directory+'/feat'):
    os.makedirs(log_directory+'/feat')
if not os.path.exists(log_directory+'/freesurfer'):
    os.makedirs(log_directory+'/freesurfer')

master.destroy()
#%%


def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        print "errors"


master = Tk()
var = []
varlist = []
subjlist = []
selection_list = dict()


def show_entry_fields():
    for ii in range(len(varlist)):
        selection_list[subjlist[ii]] = varlist[ii].get()
    master.destroy()


for i in range(len(files)):
    if files[i].find("sub") == 0:
        var = IntVar()
        Checkbutton(master, text=files[i], variable=var).grid(
            row=i+1, column=0)
        varlist.append(var)
        subjlist.append(files[i])

Button(master, text='Confirm', command=show_entry_fields).grid(
    row=i+2, column=1, sticky=W, pady=4)

mainloop()

# %%

f = open(directory+'/../scripts/subjects.txt', 'w+')


for (key, value) in selection_list.items():
    if value == 1:
        f.write(key+'\n')
f.close()

# %% preprocessing
master = Tk()


def brain_extraction():
    for (key, value) in selection_list.items():
        if value == 1:
            subj_dir = directory+'/'+key+'/'
            anat_dir = subj_dir + 'anat/'+key+'_T1w.nii.gz '
            anat_brain_dir = subj_dir + 'anat/'+key+'_T1w_brain.nii.gz '
            cmdline = "bet "+anat_dir+anat_brain_dir+"-f 0.5 -g 0 -o"
            Label(master, text='waiting for ' + key).grid(row=4, column=1)
            master.update()
            output = subprocess.check_output(cmdline, shell=True)
            Label(master, text='finished: ' + key).grid(row=4, column=1)
            master.update()
            print(output)
    # master.destroy()


def run_freesurfer():
    for (key, value) in selection_list.items():
        if value == 1:
            subj_dir = directory+'/'+key+'/'
            anat_dir = subj_dir + 'anat/'+key+'_T1w.nii.gz'
            anat_brain_dir = subj_dir + 'anat/'+key+'_T1w_brain.nii.gz'
            if os.path.exists(anat_brain_dir):
                cmdline = "echo " + "\"recon-all -i " + anat_brain_dir + " -all -subjid fs -sd " + \
                    subj_dir + " \" " + "> "+log_directory+"/freesurfer/"+key+"_fs.sh"
                Label(master, text=key + ': wrtie to sh file').grid(row=5, column=1)
                master.update()
                output = subprocess.check_output(cmdline, shell=True)
                print(output)
                Label(master, text=key +
                      ': begin to submit to cluster').grid(row=5, column=1)
                master.update()
                cmdline = "qsub -N \'fs_" + key + "\' -l \'procs=1,mem=12gb,walltime=22:00:00' " + \
                    log_directory+"/freesurfer/"+key+"_fs.sh"
                output = subprocess.check_output(cmdline, shell=True)
                print(output)
                Label(master, text=key +
                      ': finished the submission to cluster').grid(row=5, column=1)
                master.update()
            else:
                tkMessageBox.showerror("error", "No extracted brain for " +
                                       key + ", run extraction first")


def replace_word(infile, old_word, new_word):
    if not os.path.isfile(infile):
        print ("Error on replace_word, not a regular file: "+infile)
        sys.exit(1)

    f1 = open(infile, 'r').read()
    f2 = open(infile, 'w')
    m = f1.replace(old_word, new_word)
    f2.write(m)


def run_fsf():
    fsf_files = tkFileDialog.askopenfilenames(
        title='FSF files', initialdir=log_directory+'/feat', filetypes=[("fsf files", "*.fsf")])
    for fsf_file in fsf_files:
        cmdline = "echo " + "\"feat " + fsf_file + "\" > " + \
            log_directory+"/"+os.path.basename(fsf_file)+".sh"
        Label(master, text=key + ': wrtie to sh file').grid(row=17, column=1)
        master.update()
        output = subprocess.check_output(cmdline, shell=True)
        print(output)
        Label(master, text=key + ': begin to submit to cluster').grid(row=17, column=1)
        master.update()
        master.update()
        cmdline = "qsub -N \'feat_" + key + "\' -l \'procs=1,mem=12gb,walltime=22:00:00' " + \
            log_directory+"/"+os.path.basename(fsf_file)+".sh"
        output = subprocess.check_output(cmdline, shell=True)
        print(output)
        Label(master, text='finished the submission to cluster').grid(
            row=17, column=1)
        master.update()


def create_EV():
    d = Input_values(master)
    master.wait_window(d.top)


class Input_values:
    def __init__(self, parent):
        top = self.top = Toplevel(parent)
        Label(top, text="Condition Names (e.g.'cond1,cond2,cond3'):").grid(
            row=0, sticky=W)
        Button(top, text='...', command=self.more).grid(
            row=0, column=2, sticky=W)

        self.Text_Entry1 = Entry(top)
        # self.Text_Entry1.insert(END,default_cond)
        self.Text_Entry1.grid(row=0, column=1)
        if os.path.exists('./default_cond.txt'):
            cond_name_txt = open('./default_cond.txt', 'r').read().replace('\n','')
            self.Text_Entry1.insert(END, cond_name_txt)

        Label(top, text="Sesisson Num (e.g.'1,2,3,4'):").grid(row=1, sticky=W)
        self.Text_Entry2 = Entry(top)
        self.Text_Entry2.grid(row=1, column=1)

        Label(top, text="Sub Name (e.g.'sub-15'):").grid(row=2, sticky=W)
        self.Text_Entry3 = Entry(top)
        self.Text_Entry3.grid(row=2, column=1)

        self.var2 = IntVar()
        Checkbutton(top, text="Use Alter data ",
                    variable=self.var2).grid(row=4, sticky=W)

        self.var3 = IntVar()
        Checkbutton(top, text="Use Alter data (except Session 1)",
                    variable=self.var3).grid(row=5, sticky=W)

        self.var4 = IntVar()
        Checkbutton(top, text="PRF (ignore condi settings)",
                    variable=self.var4).grid(row=6, sticky=W)

        Button(top, text='Okay', command=self.ok).grid(
            row=7,      column=0, sticky=W)
        Button(top, text='Move current .feat file to old',
               command=self.move).grid(row=7,      column=2, sticky=W)

    def move(self):
        from shutil import move
        text_from_Box1 = self.Text_Entry1.get()
        print text_from_Box1
        text_from_Box2 = self.Text_Entry2.get()
        print text_from_Box2
        text_from_Box3 = self.Text_Entry3.get()
        print text_from_Box3
        EV_sessions = [x for x in text_from_Box2.split(",")]
        EV_subject = text_from_Box3
        if not os.path.exists(directory+'/'+EV_subject+'/func/old/'+strftime("%Y-%m-%d", gmtime())):
            os.makedirs(directory+'/'+EV_subject+'/func/old/' +
                        strftime("%Y-%m-%d", gmtime()))
        for EV_sess in EV_sessions:
            move(directory+'/'+EV_subject+'/func/'+EV_subject+analysisname+'_s'+EV_sess+'.feat', directory+'/' +
                 EV_subject+'/func/old/'+strftime("%Y-%m-%d", gmtime())+'/'+EV_subject+analysisname+'_s'+EV_sess+'.feat')

    def more(self):
        cond_name = tkFileDialog.askopenfilenames(
            title='Condition Names', initialdir='./', filetypes=[("txt files", "*.txt")])
        cond_name_txt = open(cond_name[0], 'r').read().replace('\n','')
        self.Text_Entry1.delete(0, END)
        self.Text_Entry1.insert(0, cond_name_txt)

    def ok(self):
        text_from_Box1 = self.Text_Entry1.get()
        print text_from_Box1
        text_from_Box2 = self.Text_Entry2.get()
        print text_from_Box2
        text_from_Box3 = self.Text_Entry3.get()
        print text_from_Box3

        EV_condis = [x for x in text_from_Box1.split(",")]
        EV_sessions = [x for x in text_from_Box2.split(",")]
        new_EV_sessions = []
        for EV_ses in EV_sessions:
            if '-' in EV_ses:
                new_EV = [x for x in EV_ses.split("-")]
                numbegin = int(new_EV[0])
                numend = int(new_EV[1])
                new_ses = range(numbegin, numend+1)
                for x in new_ses:
                    new_EV_sessions.append(str(x))
            else:
                new_EV_sessions.append(EV_ses)
        print new_EV_sessions

        EV_subject = text_from_Box3
      
        EV_alter = self.var2.get()
        EV_alter2 = self.var3.get()
        IS_PRF = self.var4.get()


        print 'EV_alter:'+str(EV_alter)
        print 'EV_alter2:'+str(EV_alter2)
        for EV_sess in new_EV_sessions:
            if not IS_PRF:
                EV1, EV2, header, footer, al = EV_replace_value(
                    directory, EV_subject, EV_sess)
                EV_conds = ''
                fsf_full = ''
                header = header.replace('EV_TOTAL', str(len(EV_condis)))
                header = header.replace('EV_2TOTAL', str(2*(len(EV_condis))))
                header = header.replace('_task_hp128_fwhm0', analysisname)
                for i in range(0, len(EV_condis)):
                    EV_cond = EV1.replace('EV_NAMEX', EV_condis[i])
                    EV_cond = EV_cond.replace('NUM_X', str(i+1))

                    for j in range(0, len(EV_condis)+1):
                        EV_2 = EV2
                        EV_2 = EV_2.replace('NUM_X', str(i+1))
                        EV_2 = EV_2.replace('NUM_Y', str(j))
                        EV_cond = EV_cond + EV_2
                    EV_conds = EV_conds + EV_cond
                if EV_alter:
                    header = header.replace('ALTER_X', '1')
                    fsf_full = fsf_full + header
                    fsf_full = fsf_full + al
                else:
                    if EV_alter2:
                        if EV_sess == '1':
                            header = header.replace('ALTER_X', '0')
                            fsf_full = fsf_full + header
                        else:
                            header = header.replace('ALTER_X', '1')
                            fsf_full = fsf_full + header
                            fsf_full = fsf_full + al
                    else:
                        header = header.replace('ALTER_X', '0')
                        fsf_full = fsf_full + header

                fsf_full = fsf_full + EV_conds
                fsf_full = fsf_full + footer
                new_file = log_directory+'/feat/'+EV_subject+'_s'+EV_sess+analysisname+'.fsf'
            else:
                prf_fsf = open('./prf','r').read()
                prf_fsf = prf_fsf.replace('DIRECTORY-X',directory)
                prf_fsf = prf_fsf.replace('SUB_X',EV_subject)
                prf_fsf = prf_fsf.replace('SESSIONX',EV_sess)
                
                EV1, EV2, header, footer, al = EV_replace_value(directory, EV_subject, EV_sess)
                prf_fsf = prf_fsf.replace('ALERT_BLOCK',al)

                fsf_full = prf_fsf
                new_file = log_directory+'/feat/'+EV_subject+'_PRF-'+EV_sess+'.fsf'

            
            text_file = open(new_file, "w")
            text_file.write(fsf_full)
            text_file.close()
        self.top.destroy()

    # NUM_X
    # NAMEX
    # DIRECTORY-X
    # SUB-X
    # SESSIONX


def EV_replace_value(directory, SUB_X,  SESSIONX):
    header = open('./header', 'r').read()
    footer = open('./footer', 'r').read()
    al = alter_content[:]
    EV1 = EV_content1[:]
    EV2 = EV_content2[:]
    header = header.replace('DIRECTORY-X', directory)
    footer = footer.replace('DIRECTORY-X', directory)
    al = al.replace('DIRECTORY-X', directory)
    EV1 = EV1.replace('DIRECTORY-X', directory)
    EV2 = EV2.replace('DIRECTORY-X', directory)

    header = header.replace('SESSIONX', SESSIONX)
    footer = footer.replace('SESSIONX', SESSIONX)
    al = al.replace('SESSIONX', SESSIONX)
    EV1 = EV1.replace('SESSIONX', SESSIONX)
    EV2 = EV2.replace('SESSIONX', SESSIONX)

    header = header.replace('SUB-X', SUB_X)

    footer = footer.replace('SUB-X', SUB_X)
    al = al.replace('SUB-X', SUB_X)
    EV1 = EV1.replace('SUB-X', SUB_X)
    EV2 = EV2.replace('SUB-X', SUB_X)

    return EV1, EV2, header, footer, al


class MyDialog:

    def __init__(self, parent):
        top = self.top = Toplevel(parent)
        Label(top, text="From sesisson:").grid(row=0, sticky=W)

        self.Text_Entry1 = Entry(top)
        self.Text_Entry1.grid(row=0, column=1)

        Label(top, text="To sesisson:").grid(row=1, sticky=W)
        self.Text_Entry2 = Entry(top)
        self.Text_Entry2.grid(row=1, column=1)

        Button(top, text='Start Calculation', command=self.ok).grid(
            row=2,      column=0, sticky=W)

    def ok(self):

        text_from_Box1 = self.Text_Entry1.get()
        print text_from_Box1
        text_from_Box2 = self.Text_Entry2.get()
        print text_from_Box2
        global from_number
        global to_numbers
        from_number = int(text_from_Box1)
        to_numbers = [int(x) for x in text_from_Box2.split(",")]

        self.top.destroy()


from time import gmtime, strftime


def reg_T1():
    for (key, value) in selection_list.items():
        if value == 1:
            if not os.path.exists(directory+"/"+key+"/masks"):
                os.makedirs(directory+"/"+key+"/masks")
    reg_time = strftime("%Y-%m-%d-%H-%M", gmtime())
    new_file = log_directory + '/''freesurfer2T1'+reg_time+'.sh'
    copy2('./register_freesurfer_V1_to_T1.sh', new_file)
    replace_word(new_file, "/project/3018012.17/${PROJECT}", directory+'/..')
    Label(master, text='wrtie to sh file').grid(row=11, column=1)
    master.update()
    cmdline = 'chmod 777 '+new_file
    output = subprocess.check_output(cmdline, shell=True)
    print(output)
    cmdline = 'bash '+new_file
    output = subprocess.check_output(cmdline, shell=True)
    print(output)
    Label(master, text='finished').grid(row=11, column=1)
    master.update()


def reg_func():
    for (key, value) in selection_list.items():
        if value == 1:
            for i in range(500):
                if not os.path.exists(directory+"/"+key+"/func/"+key+analysisname+'_s'+str(i+1)+'.feat'):
                    tkMessageBox.showinfo("Info", "Performed for session 1 to"+str(i)+"!")
                    break
                cmdline = 'flirt -in ${subj_id}_V1.nii.gz -applyxfm -init ../func/localizer_hp128_fwhm5.feat/reg/highres2example_func.mat -out ${subj_id}_V1_example_func.nii.gz -paddingsize 0.0 -interp nearestneighbour -ref ../func/localizer_hp128_fwhm5.feat/reg/example_func.nii.gz'
                cmdline = cmdline.replace(
                    '${subj_id}', directory+"/"+key+'/masks/'+key)
                cmdline = cmdline.replace('../func/localizer_hp128_fwhm5',
                                          directory+"/"+key+"/func/"+key+analysisname+'_s'+str(i+1))
                Label(master, text=key + ': begin to do V1').grid(row=12, column=1)
                master.update()
                output = subprocess.check_output(cmdline, shell=True)
                print(output)
                cmdline = cmdline.replace("_V1", "_V2")
                Label(master, text=key + ': begin to do V2').grid(row=12, column=1)
                master.update()
                output = subprocess.check_output(cmdline, shell=True)
                print(output)
                cmdline = 'fslmaths ${subj_id}_V1_example_func.nii.gz -add ${subj_id}_V2_example_func.nii.gz -bin ${subj_id}_V1V2_example_func.nii.gz'
                cmdline = cmdline.replace(
                    '${subj_id}', directory+"/"+key+'/masks/'+key)
                output = subprocess.check_output(cmdline, shell=True)
                print(output)
                Label(master, text=key + ': finished').grid(row=12, column=1)
                master.update()


Label(master, text='Selected sub:' +
      ', '.join({key for (key, value) in selection_list.items() if value == 1})).grid(row=0, column=0)

ttk.Separator(master, orient=HORIZONTAL).grid(row=1, column=0, sticky="ew")

Label(master, text='What do you want to do?').grid(row=2, column=0)
ttk.Separator(master, orient=HORIZONTAL).grid(row=3, column=0, sticky="ew")
Button(master, text='brain extraction (BET)', command=brain_extraction).grid(
    row=4, column=0, sticky=W, pady=0)
Button(master, text='Freesurfer (on cluster)', command=run_freesurfer).grid(
    row=5, column=0, sticky=W, pady=0)
ttk.Separator(master, orient=HORIZONTAL).grid(row=6, column=0, sticky="ew")
Button(master, text='V1 and V2 ==> T1', command=reg_T1).grid(
    row=7, column=0, sticky=W, pady=0)
Button(master, text='V1 and V2 ==> function', command=reg_func).grid(
    row=8, column=0, sticky=W, pady=0)

ttk.Separator(master, orient=HORIZONTAL).grid(row=9, column=0, sticky="ew")
Button(master, text='Run FSF in cluster', command=run_fsf).grid(
    row=10, column=0, sticky=W, pady=0)

Button(master, text='Create EV file to FSF', command=create_EV).grid(
    row=11, column=0, sticky=W, pady=0)

#ttk.Separator(master,orient = HORIZONTAL).grid(row=6,column=0,sticky="ew")
mainloop()
