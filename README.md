# rca-inference-pipeline

### Regularized Conditional Adversarial Network 

The Regularized Conditional Adversarial Network is used to predict average TOPro3 viabilities of organoids present in each site of a well
to generate dose response curves directly from brightfield images. </br>

In order to run inference </br>
1. clone this repo  </br>

2. `download_patient_bf.sh` is the bash script used to download the required patient line to run inference on. The data exists in `s3://mlab-microscope-data-
use1/modeling/Drug\ Assays/` </br>
  - pass the following args to download images `bash download_patient_bf.sh {Patient Line} {Drug screen} {checkpointFile} {local path to download data} {AWS PROFILE}`
</br>
  - The script will download the raw brightfield, fluorescence channel .tifs along with the checkpoint files into 3 subfolders - brightfield, fluorescence and checkpoint </br>

3. Build the docker image </br>
    `docker build -t rca_pipeline .`
    
4. Run docker container </br>
`docker run -ti --runtime=nvidia -e NVIDIA_DRIVER_CAPABILITIES=compute,utility -e NVIDIA_VISIBLE_DEVICES=all -v {path to downloaded data}:/mnt rca_pipeline` </br>


This pipeline is an adaptation of Pix2pix by Isola et al. Source code for Pix2pix - https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix </br>
