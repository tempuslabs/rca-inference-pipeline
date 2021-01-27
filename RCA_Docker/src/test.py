
import os
from options.test_options import TestOptions
from data import create_dataset
from models import create_model
from DataPrep import PreprocessData
from util.visualizer import save_images
from util import html
from pathlib import Path
import scipy.misc
import torchvision.utils
import json
from skimage.measure import compare_ssim as ssim
import numpy as np
from PIL import Image

class Inference:
    def __init__(self, TOPath, experiment_name):
        self.TOPath = TOPath
        self.TOLine = Path(self.TOPath).stem
        self.checkpoint_dir = self.TOPath
        self.experiment_name = experiment_name
        self.results_dir = Path(TOPath,str(self.TOLine+'_Results'),'results')

        self.BrightfieldPath = Path(self.TOPath,str(self.TOLine+'_Processed'), 'Brightfield')
        self.GeneratedPath = Path(self.TOPath,str(self.TOLine+'_Results'), 'GeneratedFluorescence')
        self.makedirs([self.BrightfieldPath, self.GeneratedPath, self.results_dir, self.checkpoint_dir])

        self.inferViability(self.BrightfieldPath, self.GeneratedPath, self.results_dir, self.checkpoint_dir,self.experiment_name)
    
    def makedirs(self,TOPath):
        for path in TOPath: 
            if not os.path.exists(path):
                os.makedirs(path)
            else:
                pass
        

    def saveImages(self,img, TOPath,fileName):
        torchvision.utils.save_image(img, TOPath/(str(fileName)+'.png'))

    def _toJson(self,result_dir,storeCellCount, fileName):
        with open(Path(result_dir/(str(fileName)+'.json')), 'w') as f:
            json.dump(storeCellCount, f)

    def inferViability(self, BrightfieldPath, GeneratedPath, results_dir, checkpoint_dir, experiment_name):
        print(BrightfieldPath)
        opt = TestOptions().parse()  # get test options
        # hard-code some parameters for test
        opt.num_threads = 0   # test code only supports num_threads = 1
        opt.batch_size = 1    # test code only supports batch_size = 1
        opt.serial_batches = True  # disable data shuffling; comment this line if results on randomly chosen images are needed.
        opt.no_flip = True    # no flip; comment this line if results on flipped images are needed.
        opt.num_test = len(list(BrightfieldPath.glob('**/*')))
        opt.dataroot = BrightfieldPath
        opt.checkpoints_dir = checkpoint_dir
        opt.name = experiment_name
        opt.results_dir = results_dir
        
        dataset = create_dataset(opt)  # create a dataset given opt.dataset_mode and other options
        model = create_model(opt)      # create a model given opt.model and other options
        model.setup(opt)               # regular setup: load and print networks; create schedulers
         
        # if opt.eval:
        #     print('yes')
        #     model.eval()
        storeCellCount = {}
        for i, data in enumerate(dataset):
            
            if i >= opt.num_test:  # only apply our model to opt.num_test images.
                break
            model.set_input(data)  # unpack data from data loader
            #model.test()           # run inference
            try:
                model.testCell() #runs generator (forward) and discriminator(forwardD)
                fakeCellCount = model.fake_pred_cellCount.item()
                
                #visuals = model.get_current_visuals()  # get image results
                img_path = model.get_image_paths()     # get image paths
                
                fileName = Path(img_path[0]).stem
                fake_img = model.fake_B
                self.saveImages(fake_img,GeneratedPath,fileName)
                if fileName in storeCellCount:
                
                    storeCellCount[fileName].append([fakeCellCount])
                else:
                    storeCellCount[fileName]= [fakeCellCount]
            except KeyError:
                pass
                
            if i % 5 == 0:  
                print('processing (%04d)-th image... %s' % (i, img_path))

        self._toJson(opt.results_dir,storeCellCount,'viability')



    