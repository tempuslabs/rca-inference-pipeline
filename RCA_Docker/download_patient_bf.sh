#!/bin/bash
# Takes as arguments the experiment name,folder name,checkpoint file and destination folder
# Example: bash download_patient_bf.sh LOH Assay_2A_test_CH viabilityPix2pix /data2/madhvi/Modeling/

AWS_PROFILE=$5
EXPERIMENT=$1
CHECKPOINTID=$3
FOLDERID=$2
DESTID=$4
BUCKET=s3://mlab-microscope-data-use1/modeling/Drug\ Assays/${EXPERIMENT}/${FOLDERID}/
echo ${BUCKET}
mkdir -p $DESTID
cd $DESTID
mkdir -p $FOLDERID
mkdir -p $FOLDERID/brightfield
mkdir -p $FOLDERID/checkpoint
mkdir -p $FOLDERID/fluorescent

cd $FOLDERID
#aws s3 ls ${BUCKET} --profile ${AWS_PROFILE}
 
aws s3 sync s3://mlab-microscope-data-use1/modeling/Drug\ Assays/${EXPERIMENT}/${FOLDERID}/ . --exclude "*" --include "*_w1*" --exclude "*ZStep*" --exclude "*thumb*" --profile=${AWS_PROFILE}
find . -maxdepth 5   -type f -name '*_w1*' -exec mv {} brightfield/  \;
aws s3 sync s3://mlab-microscope-data-use1/modeling/Drug\ Assays/${EXPERIMENT}/${FOLDERID}/ . --exclude "*" --include "*_w2*" --exclude "*ZStep*" --exclude "*thumb*" --profile=${AWS_PROFILE}
find . -maxdepth 5  -type f -name '*_w2*' -exec mv {} fluorescent/  \;
aws s3 sync s3://mlab-microscope-data-use1/modeling/Drug\ Assays/${EXPERIMENT}/${FOLDERID}/ . --exclude "*" --include "*_w3*" --exclude "*ZStep*" --exclude "*thumb*" --profile=${AWS_PROFILE}
find . -maxdepth 5  -type f -name '*_w3*' -exec mv {} fluorescent/  \;
aws s3 sync s3://mlab-microscope-data-use1/modeling/Drug\ Assays/${EXPERIMENT}/${FOLDERID}/ . --exclude "*" --include "*_w4*" --exclude "*ZStep*" --exclude "*thumb*" --profile=${AWS_PROFILE}
find . -maxdepth 5 -type f -name '*_w4*' -exec mv {} fluorescent/  \;
aws s3 sync s3://mlab-microscope-data-use1/modeling/Drug\ Assays/${CHECKPOINTID}/ . --include "*.pth*" --profile=${AWS_PROFILE}
find . -type f -name '*.pth*' -exec mv {} checkpoint/ \;
cd ..
rm -r $FOLDERID/2*
