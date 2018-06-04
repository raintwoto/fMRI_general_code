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
import nibabel as nib


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
        # Label(top, text="Condition Names (e.g.'cond1,cond2,cond3'):").grid(
        #     row=0, sticky=W)
        # Button(top, text='...', command=self.more).grid(
        #     row=0, column=2, sticky=W)

        # self.Text_Entry1 = Entry(top)
        # # self.Text_Entry1.insert(END,default_cond)
        # self.Text_Entry1.grid(row=0, column=1)
        # if os.path.exists('./default_cond.txt'):
        #     cond_name_txt = open('./default_cond.txt', 'r').read().replace('\n','')
        #     self.Text_Entry1.insert(END, cond_name_txt)
        Label(top, text="Sub list (e.g.'sub-8:sub-12'):").grid(row=0, sticky=W)
        self.Text_Entry3 = Entry(top)
        self.Text_Entry3.grid(row=0, column=1,sticky=W)

        Label(top, text="Sesisson Num (e.g.'1:4'):").grid(row=1, sticky=W)
        self.Text_Entry2 = Entry(top)
        self.Text_Entry2.grid(row=1, column=1,sticky=W)

        

        self.var2 = IntVar()
        Checkbutton(top, text="Use Alter data ",
                    variable=self.var2).grid(row=2, column=0,sticky=W)

        self.var3 = IntVar()
        Checkbutton(top, text="Use Alter data (except Session 1)",
                    variable=self.var3).grid(row=3, column=0,sticky=W)
        number =4
        global real_dict

        real_dict = {}
        self.variable={}
        for keyname in para_dict.keys():
            if type(para_dict[keyname]) is str:
                real_dict[keyname]= para_dict[keyname]
            elif type(para_dict[keyname]) is list:
                Label(top, text=keyname).grid(row=number, sticky=W)
                self.variable[keyname] = StringVar()
                self.variable[keyname].set(para_dict[keyname][0]) # default value                
                w = apply(OptionMenu, (top, self.variable[keyname]) + tuple(para_dict[keyname])).grid(row=number, column=1,sticky=W)
                number = number+1
            else:
                raise NameError('Parameters Incorrect')        

        ttk.Separator(top, orient=HORIZONTAL).grid(row=number+1, column=0, sticky="ew")
        ttk.Separator(top, orient=HORIZONTAL).grid(row=number+1, column=1, sticky="ew")



        Label(top, text="Contrast file:").grid(
             row=number+2, sticky=W)
        self.Text_Entry1 = Entry(top)
        self.Text_Entry1.insert(END,'NONE')
        self.Text_Entry1.grid(row=number+2, column=1,sticky=W)
        Button(top, text='...', command=self.more).grid(
             row=number+3, column=0, sticky=W)
        Button(top, text='NEW', command=self.new_contrast).grid(
             row=number+3, column=1, sticky=W)
        ttk.Separator(top, orient=HORIZONTAL).grid(row=number+4, column=0, sticky="ew")
        ttk.Separator(top, orient=HORIZONTAL).grid(row=number+4, column=1, sticky="ew")



        Button(top, text='Okay', command=self.ok).grid(
            row=number+5,      column=1, sticky=E)
        Button(top, text='Move current .feat file to old',
               command=self.move).grid(row=number+6,      column=1, sticky=E)


    def new_contrast(self):
        text_from_Box1 = self.variable['CONDNAME'].get()
        EV_condis = [x for x in text_from_Box1.split(",")]
        text = '# Leave unwanted contrast as 0\n# if you want the contrast to be ordered, keep the numbers\n#            '
        for EV_cond in EV_condis:
            text = text + EV_cond
            text = text + '\t'
        text = text + '\ncontrast = { \n'
        num=1
        for EV_cond in EV_condis:
            text = text + '\''+str(num)+'NAME' + '\':[\t'
            for EV_cond in EV_condis:
                text = text + '0,\t'
            text = text+'],\n'
            num = num+1
        text = text + '}'
        contrast_name = tkFileDialog.asksaveasfilename(
            title='Save new contrast to:', initialdir='./', filetypes=[("txt files", "*.txt")])
        #abs_path = os.path.abspath(contrast_name.name)
        open(contrast_name, 'w').write(text)
        self.Text_Entry1.delete(0, END)
        self.Text_Entry1.insert(0, contrast_name)
        tkMessageBox.showinfo("Info", "Now edit and save the new contrast file!")





    def move(self):
        from shutil import move      
        text_from_Box2 = self.Text_Entry2.get()
        print text_from_Box2
        text_from_Box3 = self.Text_Entry3.get()
        print text_from_Box3
        EV_sessions = [x for x in text_from_Box2.split(",")]

         
        new_sublist = []
        EV_subjects = [x for x in text_from_Box3.split(",")]
        for EV_subject_all in EV_subjects:
            if ':' in EV_subject_all:
                new_subject = [x for x in EV_subject_all.split(":")]
                
                new_subnum = [x for x in new_subject[0].split("-")]
                new_subnum2 = [x for x in new_subject[1].split("-")]

                
                numbegin = int(new_subnum[1])
                numend = int(new_subnum2[1])
                new_ses = range(numbegin, numend+1)
                for x in new_ses:
                    new_sublist.append('sub-'+str(x))
            else:
                new_sublist.append(EV_subject_all)
        print new_sublist

     # EV_subject = text_from_Box3
        for EV_subject in new_sublist:
            if not os.path.exists(directory+'/'+EV_subject+'/func/old/'+strftime("%Y-%m-%d", gmtime())):
                os.makedirs(directory+'/'+EV_subject+'/func/old/' +
                            strftime("%Y-%m-%d", gmtime()))
            for EV_sess in EV_sessions:
                move(directory+'/'+EV_subject+'/func/'+EV_subject+analysisname+'_s'+EV_sess+'.feat', directory+'/' +
                    EV_subject+'/func/old/'+strftime("%Y-%m-%d", gmtime())+'/'+EV_subject+analysisname+'_s'+EV_sess+'.feat')

    def more(self):
        contrast_name = tkFileDialog.askopenfilenames(
            title='Contrast file', initialdir='./', filetypes=[("txt files", "*.txt")])        
        self.Text_Entry1.delete(0, END)
        self.Text_Entry1.insert(0, contrast_name[0])

    

    def ok(self):
        global real_dict
        for keyname in para_dict.keys():
            if type(para_dict[keyname]) is list:
                real_dict[keyname] = self.variable[keyname].get()
        
        text_from_Box1 = self.variable['CONDNAME'].get()
        print text_from_Box1
        text_from_Box2 = self.Text_Entry2.get()
        print text_from_Box2
        text_from_Box3 = self.Text_Entry3.get()
        print text_from_Box3

        EV_condis = [x for x in text_from_Box1.split(",")]
        EV_sessions = [x for x in text_from_Box2.split(",")]
        new_EV_sessions = []
        for EV_ses in EV_sessions:
            if ':' in EV_ses:
                new_EV = [x for x in EV_ses.split(":")]
                numbegin = int(new_EV[0])
                numend = int(new_EV[1])
                new_ses = range(numbegin, numend+1)
                for x in new_ses:
                    new_EV_sessions.append(str(x))
            else:
                new_EV_sessions.append(EV_ses)
        print new_EV_sessions
        
        new_sublist = []
        EV_subjects = [x for x in text_from_Box3.split(",")]
        for EV_subject_all in EV_subjects:
            if ':' in EV_subject_all:
                new_subject = [x for x in EV_subject_all.split(":")]
                
                new_subnum = [x for x in new_subject[0].split("-")]
                new_subnum2 = [x for x in new_subject[1].split("-")]

                
                numbegin = int(new_subnum[1])
                numend = int(new_subnum2[1])
                new_ses = range(numbegin, numend+1)
                for x in new_ses:
                    new_sublist.append('sub-'+str(x))
            else:
                new_sublist.append(EV_subject_all)
        print new_sublist


      
        EV_alter = self.var2.get()
        EV_alter2 = self.var3.get()



        print 'EV_alter:'+str(EV_alter)
        print 'EV_alter2:'+str(EV_alter2)

        for EV_subject in new_sublist:

            for EV_sess in new_EV_sessions:
                imgshape = nib.load(directory+'/'+EV_subject+'/func/'+EV_subject+'_'+real_dict['TASKNAME']+'-'+EV_sess+'_bold.nii.gz').shape
                contrast_filename = self.Text_Entry1.get()

                real_dict['FMRI_VOLUMES'] = str(imgshape[3])
                real_dict['FMRI_TOTOALVOXELS'] = str(imgshape[0]*imgshape[1]*imgshape[2]*imgshape[3])

                if contrast_filename == 'NONE':
                    real_dict['CONTRAST_NUM'] = str(1)
                else:
                    file_in_contrast = open(contrast_filename,'r').read()
                    exec(file_in_contrast)
                    num = 0
                    for keyname in sorted(contrast.keys()):
                        if not all(x==0 for x in contrast[keyname]):
                            num = num + 1
                    real_dict['CONTRAST_NUM'] = str(num)


                EV1, EV2, header, footer, al = EV_replace_value(
                    directory, EV_subject, EV_sess)
                EV_conds = ''
                fsf_full = ''
                header = header.replace('EV_TOTAL', str(len(EV_condis)))
                header = header.replace('EV_2TOTAL', str(2*(len(EV_condis))))

                for keyname in real_dict.keys():
                    header = header.replace(keyname, real_dict[keyname])


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
                
                if contrast_filename == 'NONE':
                    fsf_full = fsf_full + footer
                else:
                    new_footer = create_footer(contrast_filename)
                    fsf_full = fsf_full + new_footer



                new_file = log_directory+'/feat/'+EV_subject+'_s'+EV_sess+'_'+real_dict['TASKNAME']+'_'+real_dict['ANALYSISNAME']+'.fsf'
        

                
                text_file = open(new_file, "w")
                text_file.write(fsf_full)
                text_file.close()
        self.top.destroy()

    # NUM_X
    # NAMEX
    # DIRECTORY-X
    # SUB-X
    # SESSIONX
def create_footer(contrast_filename):
    file_in_contrast = open(contrast_filename,'r').read()
    exec(file_in_contrast)
    text = '# Contrast & F-tests mode\n# real : control real EVs\n# orig : control original EVs\nset fmri(con_mode_old) orig\nset fmri(con_mode) orig\n'
    num = 1
    for keyname in sorted(contrast.keys()):
        if not all(x==0 for x in contrast[keyname]):
            text = text + '# Display images for contrast_real %s\nset fmri(conpic_real.%s) 1\n\n'%(str(num),str(num))
            text = text + '# Title for contrast_real %s\nset fmri(conname_real.%s) \"%s\"\n\n'%(str(num),str(num),keyname)
            cond_num =1
            for x in contrast[keyname]:
                text = text +'# Real contrast_real vector %s element %s\nset fmri(con_real%s.%s) %s\n\n# Real contrast_real vector %s element %s\
                                \nset fmri(con_real%s.%s) 0\n\n'%(str(num), str(cond_num), str(num), str(cond_num), str(x),str(num), str(cond_num+1),str(num), str(cond_num+1))
                cond_num = cond_num +2
            num = num +1
    num = 1
    for keyname in sorted(contrast.keys()):
        if not all(x==0 for x in contrast[keyname]):
            text = text + '# Display images for contrast_orig %s\n set fmri(conpic_orig.%s) 1\n\n'%(str(num),str(num))
            text = text + '# Title for contrast_orig %s\nset fmri(conname_orig.%s) \"%s\"\n\n'%(str(num),str(num),keyname)
            cond_num =1
            for x in contrast[keyname]:
                text = text +'# Real contrast_orig vector %s element %s\nset fmri(con_orig%s.%s) %s\n\n'%(str(num), str(cond_num), str(num), str(cond_num), str(x))
                cond_num = cond_num +1
            num = num +1

    text = text + '# Contrast masking - use >0 instead of thresholding?\nset fmri(conmask_zerothresh_yn) 0\n\n'
    
    for i in range(num):
        for j in range(num):
            if i!=j:
                text = text + '# Mask real contrast/F-test %s with real contrast/F-test %s?\nset fmri(conmask%s_%s) 0\n\n'%(str(i+1),str(j+1),str(i+1),str(j+1))
    text = text + short_footer
    return text





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
