#!bin/bash
# takes as argument the path to the experiment, folder, path to local data,  aws profile

EXPERIMENT=$1
FOLDERID=$2
LOCAL_PATH=$3
AWS_PROFILE=$4

extension=Results
aws s3 sync ${LOCAL_PATH}/${FOLDERID}/${FOLDERID}_${extension} s3://mlab-microscope-data-use1/modeling/Drug\ Assays/${EXPERIMENT}/${FOLDERID}/${FOLDERID}_${extension}/ --profile ${AWS_PROFILE}
echo done


