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
import os
from shutil import *
import subprocess
import re


f1 = open('./gui_preprocessing_config', 'r').read()
exec(f1)


master = Tk()
directory = tkFileDialog.askdirectory(
    title="Select data Directory", initialdir=initialdir)

if not os.path.exists(directory+'/../logs/feat'):
    os.makedirs(directory+'/../logs/feat')
if not os.path.exists(directory+'/../logs/freesurfer'):
    os.makedirs(directory+'/../logs/freesurfer')

files = os.listdir(directory)
log_directory = tkFileDialog.askdirectory(
    title="Select a Log Directory", initialdir=directory+'/../logs/')
master.destroy()
#%%


def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        print "errors"


file_text = open(directory+'/../logs/feat/'+template_filename, 'r')
text = file_text.read()
template_output_dir = find_between(text, 'set fmri(outputdir) "', '"')
template_project_dir = find_between(text, 'set highres_files(1) "', '/sub')
template_subjname_beh = find_between(text, '/info/', '_s')
template_subjname = find_between(text, '/data/', '/func')
template_4dfile = find_between(text, 'set feat_files(1) "', '"')


prf_file_text = open(directory+'/../logs/feat/'+prf_template_filename, 'r')
text = prf_file_text.read()
prf_template_output_dir = find_between(text, 'set fmri(outputdir) "', '"')
prf_template_subjname = find_between(text, '/data/', '/func')
prf_template_4dfile = find_between(text, 'set feat_files(1) "', '"')


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

f = open(directory+'/../subjects.txt', 'w+')


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


def create_GLM():
    for (key, value) in selection_list.items():
        if value == 1:
            beh = tkFileDialog.askopenfilename(
                title="Select first file for session 1 for:" + key, initialdir=directory+'/'+key+'/info/')
            if beh.find(condi[0]) == -1:
                tkMessageBox.showerror("error", "selection not correct!")
                break
            else:
                for i in range(sesnum):
                    new_file = directory+'/../logs/feat/' + \
                        key+'_s'+str(i+1)+analysisname+'.fsf'
                    if not os.path.exists(new_file):
                        copy2(directory+'/../logs/feat/' +
                              template_filename, new_file)
                    else:
                        results = tkMessageBox.askquestion(
                            "Same", "Analysis "+key+'_s'+str(i+1)+analysisname+" fsf file exists, do it again?", icon='warning')
                        if results == 'no':
                            break
                        else:
                            copy2(directory+'/../logs/feat/' +
                                  template_filename, new_file)

                    start_s = '/info/'
                    end_s = '_s1'
                    subjname_beh = beh[beh.find(
                        start_s)+len(start_s):beh.rfind(end_s)]
                    replace_word(new_file, "set fmri(outputdir) \""+template_output_dir+"\"",
                                 "set fmri(outputdir) \""+directory+"/"+key+"/func/"+key+analysisname+'_s'+str(i+1)+"\"")
                    replace_word(new_file, template_subjname_beh, subjname_beh)
                    replace_word(new_file, template_project_dir, directory)
                    new_4dfile = template_4dfile.replace(
                        template_sesname, sesname[i])
                    replace_word(new_file, template_4dfile, new_4dfile)
                    replace_word(new_file, template_subjname, key)

                    for k in range(0, len(template_condi)):
                        replace_word(new_file, template_condi[k], condi[k])
                    for k in range(0, len(template_other)):
                        replace_word(new_file, template_other[k], new_other[k])

                    for cond in condi:
                        beh_new = beh.replace(condi[0], cond)
                        beh_ses = beh_new.replace('s1', 's'+str(i+1))
                        replace_word(new_file, beh_new, beh_ses)
                    if i > 0:
                        replace_word(new_file, 'set fmri(alternateReference_yn) 0',
                                     'set fmri(alternateReference_yn) 1')
                        replace_word(new_file, 'set fmri(confoundevs) 0', "set fmri(confoundevs) 0\n\n# Session's alternate reference image for analysis 1 \nset alt_ex_func(1) \"" +
                                     directory+"/"+key+"/func/"+key+analysisname+'_s1.feat/example_func.nii.gz\"')
                        #not finished
                Label(master, text='finished: ' + key).grid(row=7, column=1)
                master.update()


def run_ses_1():
    for (key, value) in selection_list.items():
        if value == 1:
            i = 0
            if os.path.exists(directory+key+'/func/'+key+analysisname+'_s'+str(i+1)+'.feat') or os.path.exists(directory+key+'/func/'+key+analysisname+'_s'+str(i+1)+'.gfeat'):
                results = tkMessageBox.askquestion(
                    "Same", "Analysis"+key+analysisname+" exists, do it again?", icon='warning')
                if results == 'no':
                    break
            fsf_file = directory+'/../logs/feat/' + \
                key+'_s'+str(i+1)+analysisname+'.fsf'
            if not os.path.exists(fsf_file):
                tkMessageBox.showerror("error", "fsf file for "+key+'_s' +
                                       str(i+1)+analysisname+' doesn\'t exist')

            cmdline = "echo " + "\"feat " + fsf_file + "\" > " + \
                log_directory+"/"+key+'_s'+str(i+1)+analysisname+".sh"
            Label(master, text=key + ': wrtie to sh file').grid(row=8, column=1)
            master.update()
            output = subprocess.check_output(cmdline, shell=True)
            print(output)
            Label(master, text=key +
                  ': begin to submit to cluster').grid(row=8, column=1)
            master.update()
            master.update()
            cmdline = "qsub -N \'feat_" + key + "\' -l \'procs=1,mem=12gb,walltime=22:00:00' " + \
                log_directory+"/"+key+'_s'+str(i+1)+analysisname+".sh"
            output = subprocess.check_output(cmdline, shell=True)
            print(output)
            Label(master, text=key +
                  ': finished the submission to cluster').grid(row=8, column=1)
            master.update()


def run_ses_else():

    log_directory = tkFileDialog.askdirectory(
        title="Select a Log Directory", initialdir=directory+'/../logs/feat')
    for (key, value) in selection_list.items():
        if value == 1:
            if not os.path.exists(directory+"/"+key+"/func/"+key+analysisname+'_s1.feat/example_func.nii.gz'):
                tkMessageBox.showerror(
                    "error", "example_fun.nii.gz not exist yet, wait ses 1 run")
                break
            for i in range(1, sesnum):
                if os.path.exists(directory+key+'/func/'+key+analysisname+'_s'+str(i+1)+'.feat') or os.path.exists(directory+key+'/func/'+key+analysisname+'_s'+str(i+1)+'.gfeat'):
                    results = tkMessageBox.askquestion(
                        "Same", "Analysis"+key+analysisname+" exists, do it again?", icon='warning')
                    if results == 'no':
                        break
                fsf_file = directory+'/../logs/feat/' + \
                    key+'_s'+str(i+1)+analysisname+'.fsf'
                if not os.path.exists(fsf_file):
                    tkMessageBox.showerror("error", "fsf file for "+key+'_s' +
                                           str(i+1)+analysisname+' doesn\'t exist')

                cmdline = "echo " + "\"feat " + fsf_file + "\" > " + \
                    log_directory+"/"+key+'_s'+str(i+1)+analysisname+".sh"
                Label(master, text=key + ': wrtie to sh file').grid(row=9, column=1)
                master.update()
                output = subprocess.check_output(cmdline, shell=True)
                print(output)
                Label(master, text=key +
                      ': begin to submit to cluster').grid(row=9, column=1)
                master.update()
                master.update()
                cmdline = "qsub -N \'feat_" + key + "\' -l \'procs=1,mem=12gb,walltime=22:00:00' " + \
                    log_directory+"/"+key+'_s'+str(i+1)+analysisname+".sh"
                output = subprocess.check_output(cmdline, shell=True)
                print(output)
                Label(master, text=key +
                      ': finished the submission to cluster').grid(row=9, column=1)
                master.update()


def run_fsf():
    if not os.path.exists(directory+'/../logs/feat'):
        os.makedirs(directory+'/../logs/feat')
    log_directory = tkFileDialog.askdirectory(
        title="Select a Log Directory", initialdir=directory+'/../logs/feat')
    fsf_files = tkFileDialog.askopenfilenames(
        title='FSF files', initialdir=directory+'/../logs/feat', filetypes=[("fsf files", "*.fsf")])
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

        self.Text_Entry1 = Entry(top)
        self.Text_Entry1.insert(END,default_cond)
        self.Text_Entry1.grid(row=0, column=1)

        Label(top, text="Sesisson Num (e.g.'1,2,3,4'):").grid(row=1, sticky=W)
        self.Text_Entry2 = Entry(top)
        self.Text_Entry2.grid(row=1, column=1)

        Label(top, text="Sub Name (e.g.'sub-15'):").grid(row=2, sticky=W)
        self.Text_Entry3 = Entry(top)
        self.Text_Entry3.grid(row=2, column=1)

        self.var2 = IntVar()
        Checkbutton(top, text="Use Alter data ",
                    variable=self.var2).grid(row=3, sticky=W)

        self.var3 = IntVar()
        Checkbutton(top, text="Use Alter data (except Session 1)",
                    variable=self.var3).grid(row=4, sticky=W)

        Button(top, text='Okay', command=self.ok).grid(
            row=5,      column=0, sticky=W)
        Button(top, text='Move current .feat file to old',
               command=self.move).grid(row=5,      column=2, sticky=W)

    def move(self):
        from shutil import move
        text_from_Box1 = self.Text_Entry1.get()
        print text_from_Box1
        text_from_Box2 = self.Text_Entry2.get()
        print text_from_Box2
        text_from_Box3 = self.Text_Entry3.get()
        print text_from_Box3
        EV_condis = [x for x in text_from_Box1.split(",")]
        EV_sessions = [x for x in text_from_Box2.split(",")]
        EV_subject = text_from_Box3
        if not os.path.exists(directory+'/'+EV_subject+'/func/old/'+strftime("%Y-%m-%d", gmtime())):
            os.makedirs(directory+'/'+EV_subject+'/func/old/' +
                        strftime("%Y-%m-%d", gmtime()))
        for EV_sess in EV_sessions:
            move(directory+'/'+EV_subject+'/func/'+EV_subject+analysisname+'_s'+EV_sess+'.feat', directory+'/' +
                 EV_subject+'/func/old/'+strftime("%Y-%m-%d", gmtime())+'/'+EV_subject+analysisname+'_s'+EV_sess+'.feat')

    def ok(self):

        text_from_Box1 = self.Text_Entry1.get()
        print text_from_Box1
        text_from_Box2 = self.Text_Entry2.get()
        print text_from_Box2
        text_from_Box3 = self.Text_Entry3.get()
        print text_from_Box3

        EV_condis = [x for x in text_from_Box1.split(",")]
        EV_sessions = [x for x in text_from_Box2.split(",")]
        EV_subject = text_from_Box3
        EV_alter = self.var2.get()
        EV_alter2 = self.var3.get()

        print 'EV_alter:'+str(EV_alter)
        print 'EV_alter2:'+str(EV_alter2)
        for EV_sess in EV_sessions:
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

            new_file = directory+'/../logs/feat/'+EV_subject+'_s'+EV_sess+analysisname+'.fsf'
            text_file = open(new_file, "w")
            text_file.write(fsf_full)
            text_file.close()
        self.top.destroy()

    # NUM_X
    # NAMEX
    # DIRECTORY-X
    # SUB-X
    # SESSIONX


def EV_replace_value(directory, SUB_X, SESSIONX):
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


def generlaize_fsf():
    if not os.path.exists(directory+'/../logs/feat'):
        os.makedirs(directory+'/../logs/feat')
    log_directory = tkFileDialog.askdirectory(
        title="Where to save", initialdir=directory+'/../logs/feat')
    fsf_file = tkFileDialog.askopenfilename(
        title='FSF files', initialdir=directory+'/../logs/feat', filetypes=[("fsf files", "*.fsf")])

    d = MyDialog(master)
    master.wait_window(d.top)

    for to_num in to_numbers:
        new_file = fsf_file.replace('_s'+str(from_number), '_s'+str(to_num))
        if not os.path.exists(new_file):
            copy2(fsf_file, new_file)
        else:
            results = tkMessageBox.askquestion("Same", os.path.basename(
                new_file)+" exists, rewrite it?", icon='warning')
            if results == 'no':
                break
            else:
                copy2(fsf_file, new_file)
        replace_word(new_file, '_s'+str(from_number), '_s'+str(to_num))


from time import gmtime, strftime


def reg_T1():
    for (key, value) in selection_list.items():
        if value == 1:
            if not os.path.exists(directory+"/"+key+"/masks"):
                os.makedirs(directory+"/"+key+"/masks")
    log_directory = tkFileDialog.askdirectory(
        title="Select a Log Directory for registeration", initialdir=directory+'/../logs/reg')
    reg_time = strftime("%Y-%m-%d-%H-%M", gmtime())
    new_file = log_directory + '/''freesurfer2T1'+reg_time+'.sh'
    copy2(directory+'/../scripts/preprocessing/localizer/register_freesurfer_V1_to_T1.sh', new_file)
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
            for i in range(sesnum):
                if not os.path.exists(directory+"/"+key+"/func/"+key+analysisname+'_s'+str(i+1)+'.feat'):
                    tkMessageBox.showerror("error", "feat "+key+analysisname +
                                           '_s'+str(i+1)+"not complete!")
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


def create_GLM_prf():
    for (key, value) in selection_list.items():
        if value == 1:
            for i in range(prfnum):
                new_file = directory+'/../logs/feat/'+key+'_'+prfname[i]+'.fsf'
                if not os.path.exists(new_file):
                    copy2(directory+'/../logs/feat/' +
                          prf_template_filename, new_file)
                else:
                    results = tkMessageBox.askquestion(
                        "Same", "Analysis "+key+prfname[i]+" fsf file exists, do it again?", icon='warning')
                    if results == 'no':
                        break
                    else:
                        copy2(directory+'/../logs/feat/' +
                              prf_template_filename, new_file)

                prf_template_project_dir.replace('sub-x',key)
                replace_word(new_file, prf_template_project_dir, directory)
                replace_word(new_file, "set fmri(outputdir) \""+prf_template_output_dir +
                             "\"", "set fmri(outputdir) \""+directory+"/"+key+"/func/"+prfname[i]+"\"")
                new_4dfile = prf_template_4dfile.replace(
                    prf_template_sesname, prfname[i])
                replace_word(new_file, prf_template_4dfile, new_4dfile)
                replace_word(new_file, prf_template_subjname, key)


#                 if i>0:
#                     replace_word(new_file,'set fmri(alternateReference_yn) 0','set fmri(alternateReference_yn) 1')
#                     replace_word(new_file,'set fmri(confoundevs) 0', "set fmri(confoundevs) 0\n\n# Session's alternate reference image for analysis 1 \nset alt_ex_func(1) \""+directory+"/"+key+"/func/"+key+analysisname+'_s1.feat/example_func.nii.gz\"')
                #not finished
            Label(master, text='finished: ' + key).grid(row=14, column=1)
            master.update()


def run_pRF():
    log_directory = tkFileDialog.askdirectory(
        title="Select a Log Directory", initialdir=directory+'/../logs/')
    for (key, value) in selection_list.items():
        if value == 1:
            if not os.path.exists(directory+"/"+key+"/func/"+key+analysisname+'_s1.feat/example_func.nii.gz'):
                tkMessageBox.showerror(
                    "error", "example_fun.nii.gz not exist yet, wait ses 1 run")
                break
            for i in range(0, sesnum):
                if os.path.exists(directory+key+'/func/'+key+"_"+prfname[i]+'.feat'):
                    results = tkMessageBox.askquestion(
                        "Same", "Analysis"+prfname[i]+" exists, do it again?", icon='warning')
                    if results == 'no':
                        break
                fsf_file = log_directory+'/feat/'+key+"_"+prfname[i]+'.fsf'
                if not os.path.exists(fsf_file):
                    tkMessageBox.showerror(
                        "error", "fsf file for "+prfname[i]+' doesn\'t exist')

                cmdline = "echo " + "\"feat " + fsf_file + "\" > " + \
                    log_directory+"/"+key+"_"+prfname[i]+".sh"
                Label(master, text=key +
                      ': wrtie to sh file').grid(row=15, column=1)
                master.update()
                output = subprocess.check_output(cmdline, shell=True)
                print(output)
                Label(master, text=key +
                      ': begin to submit to cluster').grid(row=15, column=1)
                master.update()
                master.update()
                cmdline = "qsub -N \'feat_" + key + "\' -l \'procs=1,mem=12gb,walltime=22:00:00' " + \
                    log_directory+"/"+key+"_"+prfname[i]+".sh"
                output = subprocess.check_output(cmdline, shell=True)
                print(output)
                Label(master, text=key +
                      ': finished the submission to cluster').grid(row=15, column=1)
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
Button(master, text='Create GLM file', command=create_GLM).grid(
    row=7, column=0, sticky=W, pady=0)
Button(master, text='Run Sesion 1 (on cluster)', command=run_ses_1).grid(
    row=8, column=0, sticky=W, pady=0)
Button(master, text='Run Other Sesions ', command=run_ses_else).grid(
    row=9, column=0, sticky=W, pady=0)
ttk.Separator(master, orient=HORIZONTAL).grid(row=10, column=0, sticky="ew")
Button(master, text='V1 and V2 ==> T1', command=reg_T1).grid(
    row=11, column=0, sticky=W, pady=0)
Button(master, text='V1 and V2 ==> function', command=reg_func).grid(
    row=12, column=0, sticky=W, pady=0)

ttk.Separator(master, orient=HORIZONTAL).grid(row=13, column=0, sticky="ew")
Button(master, text='Create GLM file: PRF', command=create_GLM_prf).grid(
    row=14, column=0, sticky=W, pady=0)
Button(master, text='Run pRF pre-processing',
       command=run_pRF).grid(row=15, column=0, sticky=W, pady=0)

ttk.Separator(master, orient=HORIZONTAL).grid(row=16, column=0, sticky="ew")
Button(master, text='Run FSF in cluster', command=run_fsf).grid(
    row=17, column=0, sticky=W, pady=0)
Button(master, text='Generalize FSF file', command=generlaize_fsf).grid(
    row=18, column=0, sticky=W, pady=0)
Button(master, text='Create EV file to FSF', command=create_EV).grid(
    row=19, column=0, sticky=W, pady=0)

#ttk.Separator(master,orient = HORIZONTAL).grid(row=6,column=0,sticky="ew")
mainloop()
