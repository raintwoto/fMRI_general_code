#!/bin/bash

#
# register V1 & V2 from Freesurfer parcellation to the functional data
# Author: M Ekman August 2017

PROJECT="fMRI_EXAMPLE_PROJECT/PROJECT1"

project_path="/project/3018035.03/fMRI/Popout/data/.."
subject_list="${project_path}/scripts/subjects.txt"
log_path="${project_path}/logs/freesurfer"
# --------------------------------------------------------------------------- #

declare -a LABELS=(V1 V2)

cwd=`pwd`

# read all subject IDs 
SUBJECTS="$( cat ${subject_list} )"

for subj_id in ${SUBJECTS[@]} ; do
	cd ${project_path}/data/${subj_id}/fs
	if [ ! -f ${logs_path}/${subj_id}_register_freesurfer_V1_to_functional_data ] ; then

		echo "" > ${logs_path}/${subj_id}_register_freesurfer_V1_to_functional_data
		echo ">> running tkregister for subject $subj_id (Freesurfer -> T1)"

		SUBJ_DIR="${project_path}/data/${subj_id}"
		ANAT="${project_path}/data/${subj_id}/anat/${subj_id}_anat.nii.gz"
		export SUBJECTS_DIR=""
		export SUBJECTS_DIR=${SUBJ_DIR}

		if [ ! -f ${project_path}/data/${subj_id}/fs/register.dat ] ; then
			bbregister --s fs --mov ${ANAT} --reg register.dat --init-fsl --t1
		fi

		tkregister2 --mov ${project_path}/data/${subj_id}/fs/mri/rawavg.mgz --noedit --s fs --sd ${SUBJ_DIR} --regheader --reg ${project_path}/data/${subj_id}/fs/register.dat

		for label in ${LABELS[@]} ; do
			mri_label2vol --label ${project_path}/data/${subj_id}/fs/label/lh.${label}.label --temp ${project_path}/data/${subj_id}/fs/mri/rawavg.mgz --subject fs --hemi lh --o ${project_path}/data/${subj_id}/masks/${subj_id}_lh_${label}.nii.gz --proj frac 0 1 .1 --fillthresh 0 --reg ${project_path}/data/${subj_id}/fs/register.dat
			mri_label2vol --label ${project_path}/data/${subj_id}/fs/label/rh.${label}.label --temp ${project_path}/data/${subj_id}/fs/mri/rawavg.mgz --subject fs --hemi rh --o ${project_path}/data/${subj_id}/masks/${subj_id}_rh_${label}.nii.gz --proj frac 0 1 .1 --fillthresh 0 --reg ${project_path}/data/${subj_id}/fs/register.dat
			fslmaths ${project_path}/data/${subj_id}/masks/${subj_id}_rh_${label}.nii.gz -add ${project_path}/data/${subj_id}/masks/${subj_id}_lh_${label}.nii.gz -bin ${project_path}/data/${subj_id}/masks/${subj_id}_${label}.nii.gz
		done

	else
	    echo " >> skipping, data already processed"
	fi

	
done


# NB, The page: http://ftp.nmr.mgh.harvard.edu/fswiki/mri_label2vol offers little information. More detailed information about the functions can be found be by typing in the terminal <function> --help. For example: mri_label2vol --help
# http://brainybehavior.com/neuroimaging/2010/05/converting-cortical-labels-from-freesurfer-to-volumetric-masks/

# Project the label along the surface normal. type can be abs or frac.
# abs means that the start, stop, and delta are measured in mm. frac
# means that start, stop, and delta are relative to the thickness at
# each vertex. The label definition is changed to fill in label
# points in increments of delta from start to stop. Requires subject
# and hemi in order to load in a surface and thickness. Uses the
# white surface. The label MUST have been defined on the surface.
#
# --fillthresh thresh
# Relative threshold which the number hits in a voxel must exceed for
# the voxel to be considered a candidate for membership in the label. A
# 'hit' is when a label point falls into a voxel. thresh is a value
# between 0 and 1 indicating the fraction of the voxel volume that must
# be filled by label points. The voxel volume is determined from the
# template. It is assumed that the each label point represents a voxel
# 1mm3 in size (which can be changed with --labvoxvol). So, the actual
# number of hits needed to exceed threshold is
# thresh*TempVoxVol/LabVoxVol. The default value is 0, meaning that any
# label point that falls into a voxel makes that voxel a candidate for
# membership in the label.  Note: a label must also have the most hits
# in the voxel before that voxel will actually be assigned to the label
# in the volume. Note: the label voxel volume becomes a little ambiguous
# for surface labels, particularly when they are 'filled in' with
# projection.
