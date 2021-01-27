import os
from optparse import OptionParser
import pandas as pd
import numpy as np
from glob import glob
#import openslide as osi
from PIL import Image
import matplotlib.pyplot as plt
from skimage import exposure
#import cv2
from scipy import stats
from skimage import img_as_ubyte
from pathlib import Path 

class PreprocessData:
    #check if fluorescence readout exists and flag 
    def __init__(self, TOPath=None):
        """ Takes in the main path containing the raw tifs for a particular TO Line
        - Create brightfield and fluor dict 
            {key : value ==> filename : path to tif file}
            Brightfield dict-{'LOH_O02_s2': [PosixPath('/data2/madhvi/Modeling/fluorescent_response_model/RCA_Docker_test/NU-CO-066/brightfield/LOH_O02_s2_w148CC484A-0837-414F-A6D6-3A16C0FEEDFA.tif')]}
            Fluorescent dict-{'LOH_O02_s2': [PosixPath('/data2/madhvi/Modeling/fluorescent_response_model/RCA_Docker_test/NU-CO-066/fluorescent/LOH_O02_s2_w2448D6101-93D8-44EA-83FC-995F7F7B693B.tif'), 
                                            PosixPath('/data2/madhvi/Modeling/fluorescent_response_model/RCA_Docker_test/NU-CO-066/fluorescent/LOH_O02_s2_w43F14E192-1A51-4D85-9467-0664C603EBF0.tif'), 
                                            PosixPath('/data2/madhvi/Modeling/fluorescent_response_model/RCA_Docker_test/NU-CO-066/fluorescent/LOH_O02_s2_w3F98DDD46-9869-4A73-8BDB-8EF31DE10453.tif')]}
        - Contrast enhance the brightfield images
        - Contrast enhance the fluorescent readouts
        - Save the brightfied enhanced images in the Brightfield subdirectory 
        - Save individual channel enhanced images (into subdirectories `DeadNuclei, AllNuclei, ApoptoticNuclei`) as well as combined fluorescence readouts(Combined) 
        """
        self.TOPath = Path(TOPath)
        self.TOLine = self.TOPath.stem
       
        #path to the raw tifs
        self._brightfieldPath = Path(TOPath, 'brightfield')
        self._fluorescentPath = Path(TOPath, 'fluorescent')
        self._outputPath = Path(TOPath, str(self.TOLine)+ '_Processed')
        self._makedirs([self._brightfieldPath, self._fluorescentPath, self._outputPath])
        
        if not os.listdir(self._outputPath):
            #store the brightfield and fluorescent channels in two dicts
            self.fluorDict = self._getfluor(self._fluorescentPath)
            self.brightDict = self._getBF(self._brightfieldPath)
            
            
            #enhance contrast
            for img in self.brightDict:
                self._enhanceBrightfield(self.brightDict[img], self._outputPath, img)
                self._enhanceFluorescent(self.fluorDict[img], self._outputPath, img)
        else:

            print('Preprocessing done!')
            pass
            
        #concatenate brightfield and fluorescent
        #self.combineBrightFluor(self._outputPath, 'Brightfield', 'CombinedFluorescence')
    def _makedirs(self, TOPath):

        for path in TOPath:
           
            if not os.path.exists(path):
                os.makedirs(path)
            else:
                pass

    def _openImage(self, sample):
        sample = Image.open(sample)
        imarray = np.array(sample)
        return imarray

    def _getRange(self, img):
        """ This function gets the inner and outer bounds (range) to enhance contrast of each fluorescent image
        -it bins the pixel intensities into 10 bins and chooses the mode of the first bin as the inner range, and the intensity
        at the first bin edge as outer range"""
        img= img.flatten()
        #get distribution
        hist, edges = np.histogram(img, bins=10,density=True)
        hist_index=np.where(hist)[0]
        in_range = stats.mode(img)[0]
        in_range = in_range[0]
        out_range=edges[hist_index[1]]

        return in_range, out_range


    def _convert_to_img(self, img):
        #converts fluorescent image to 0-255 pixel intensity values
        #don't convert the tifs to 0-255(do contrast adjustment on the original tif)
        img_convert = img_as_ubyte(img)
        img_convert = img_convert.astype(np.uint8)
        img_convert=np.array(img_convert)
        return img_convert

    def _getBF(self, bf_path):
        list_files = [e for e in bf_path.iterdir() if e.is_file()]
        BrightField = {}
        
        for tif in list_files:
            basename = os.path.basename(tif)
            basename1 = basename.split('.')[0]
            assayKey = basename.split('_')[:-1]
            assayKey = '_'.join(assayKey)
            assayValue = basename.split('_')[-1]
            tifFile = assayKey+'_'+assayValue
            if assayKey in BrightField:
                if assayValue.find('w1')==0:
                    BrightField[assayKey].append(bf_path/str(tifFile))
            else:
                if assayValue.find('w1')==0:
                    BrightField[assayKey] = [bf_path/str(tifFile)]
        return BrightField

    def _getfluor(self, modeling_path):
        
        list_files = [e for e in modeling_path.iterdir() if e.is_file()]
        #ist_files =list(glob(modeling_path))
        #print(list_files)
        fluor = {}

        for tif in list_files:
            basename = os.path.basename(tif)
            basename = basename.split('.')[0]
            assayKey = basename.split('_')[:-1]
            assayKey = '_'.join(assayKey)
            assayValue = basename.split('_')[-1]
            tifFile = assayKey+'_'+assayValue+'.tif'
            if assayKey in fluor:
                #dont add the brightfield image in the dictionary 
                
                if assayValue.find('w1')==-1:
                    
                    fluor[assayKey].append(modeling_path/str(tifFile))
            else:
                if assayValue.find('w1')==-1:
                    fluor[assayKey] = [modeling_path/str(tifFile)]

        return fluor

    def _enhanceContrast(self,img, in_range, out_range):
        img = exposure.rescale_intensity(img, in_range=(in_range, out_range))
        return img

    def _enhanceBrightfield(self, img, bf_out, key):
        #check the 99th percentile for upper range 
        bfPath = Path(bf_out, 'Brightfield')
        self._makedirs([bfPath])
        bf_img = img[0]
        bf_img = self._openImage(bf_img)
        bf_img = self._convert_to_img(bf_img)
        p2, p98 = np.percentile(bf_img.flatten(), [2, 98])
        
        img_enhance = self._enhanceContrast(bf_img, p2, p98)
        img_enhance = Image.fromarray(img_enhance)
        img_enhance.save(bfPath/(str(key)+'.png'))
        return img_enhance 

    def _enhanceFluorescent(self, imageList, imagePath, key):
        redPath = Path(imagePath, 'DeadNuclei')
        bluePath = Path(imagePath, 'allNuclei')
        greenPath = Path(imagePath,'ApoptoticNuclei')
        combinedPath = Path(imagePath, 'CombinedFluorescence')
        self._makedirs([redPath, bluePath, greenPath, combinedPath])
        for image in imageList:
            #make function call 
            if str(image).find('w2')>0:
                img1 = self._openImage(image)
                img1 = self._convert_to_img(img1)
                in_range, out_range = self._getRange(img1)
                img1 = self._enhanceContrast(img1, in_range+3, out_range+2)
                img1 = Image.fromarray(img1)
                img1.save(bluePath/(str(key)+'.png'))
            if str(image).find('w3')>0:
                img2 = self._openImage(image)
                img2 = self._convert_to_img(img2)
                in_range, out_range = self._getRange(img2)
                img2 = self._enhanceContrast(img2, in_range+2, out_range+1)
                img2 = Image.fromarray(img2)
                img2.save(greenPath/(str(key)+'.png'))
            if str(image).find('w4')>0:
                img3= self._openImage(image)
                img3 = self._convert_to_img(img3)
                in_range, out_range = self._getRange(img3)
                img3 = self._enhanceContrast(img3, in_range+2, out_range+1)
                img3 = Image.fromarray(img3)
                img3.save(redPath/(str(key)+'.png'))
 
        imgCombine = np.dstack((img3, img2, img1))
        imgCombine = Image.fromarray(imgCombine)
        imgCombine.save(combinedPath/(str(key)+'.png'))
    
    # def combineBrightFluor(self,ProcessedPath, _brightfield, _fluorescence):
    #     TOLine = ProcessedPath.stem
    #     BrightPath = Path(ProcessedPath, _brightfield)
    #     FluorPath = Path(ProcessedPath, _fluorescence)
    #     combinedPath = ProcessedPath/(str(TOLine)+'-gan')
    #     print(combinedPath)
    #     self._makedirs([BrightPath, FluorPath, combinedPath])
        
    #     imgList = os.listdir(BrightPath)
    #     #luorList = os.listdir(FluorPath)
        
    #     #assert condition to check if number of bf and fluor images are equal 

    #     #log images that dont have a pair

    #     #enumerate list of images
    #     for n in range(len(imgList)):
    #         name_A = imgList[n]
    #         path_A = Path(BrightPath, name_A)

    #         name_B = name_A
    #         path_B = Path(FluorPath, name_B)
            
    #         if path_A.is_file() and path_B.is_file():
                
    #             im_A = cv2.imread(str(path_A), 1) # python2: cv2.CV_LOAD_IMAGE_COLOR; python3: cv2.IMREAD_COLOR
    #             im_B = cv2.imread(str(path_B), 1) # python2: cv2.CV_LOAD_IMAGE_COLOR; python3: cv2.IMREAD_COLOR
    #             im_AB = np.concatenate([im_A, im_B], 1)
    #             imgAB = Image.fromarray(im_AB)
    #             imgAB.save(combinedPath/(str(name_A)))


       

    
    
    
 
    
    