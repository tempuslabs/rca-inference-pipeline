import os.path
from data.base_dataset import BaseDataset, get_params, get_transform
from data.image_folder import make_dataset,getcellCountDict
from PIL import Image
from pathlib import Path
import torch

class AlignedDataset(BaseDataset):
    """A dataset class for paired image dataset.

    It assumes that the directory '/path/to/data/train' contains image pairs in the form of {A,B}.
    During test time, you need to prepare a directory '/path/to/data/test'.
    """

    def __init__(self, opt):
        """Initialize this dataset class.

        Parameters:
            opt (Option class) -- stores all the experiment flags; needs to be a subclass of BaseOptions
        """
        BaseDataset.__init__(self, opt)
        self.dir_AB = os.path.join(opt.dataroot)  # get the image directory
        self.AB_paths = sorted(make_dataset(self.dir_AB, opt.max_dataset_size))  # get image paths
        assert(self.opt.load_size >= self.opt.crop_size)   # crop_size should be smaller than the size of loaded image
        self.input_nc = self.opt.output_nc if self.opt.direction == 'BtoA' else self.opt.input_nc
        self.output_nc = self.opt.input_nc if self.opt.direction == 'BtoA' else self.opt.output_nc

    def __getitem__(self, index):
        """Return a data point and its metadata information.

        Parameters:
            index - - a random integer for data indexing

        Returns a dictionary that contains A, B, A_paths and B_paths
            A (tensor) - - an image in the input domain
           
            A_paths (str) - - image paths
           
        """
        # read a image given a random integer index

        AB_path = self.AB_paths[index]
        fileName = Path(AB_path).name
        
        #viability = self.cellCount[str(fileName)]
        
        AB = Image.open(AB_path).convert('RGB')
       

        # apply the same transform to both A and B
        transform_params = get_params(self.opt, AB.size)
        A_transform = get_transform(self.opt, transform_params, grayscale=(self.input_nc == 1))
        A = A_transform(AB)
        
        return {'A': A, 'A_paths': AB_path}

    def __len__(self):
        """Return the total number of images in the dataset."""
        return len(self.AB_paths)
