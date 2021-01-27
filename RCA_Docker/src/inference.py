#!usr/bin/env python3

import json
from pathlib import Path
import pandas as pd
import numpy as np
from optparse import OptionParser
import re
import os
from glob import glob
from options.test_options import TestOptions
from DataPrep import PreprocessData
from test import Inference

prefix=Path('/mnt')
input_data= Path(prefix)
input_data.mkdir(parents=True, exist_ok=True)


if __name__=="__main__":
    # usage = "usage: python inference.py "
    # parser = OptionParser(usage)
    TOData = os.listdir(input_data)
    TOData = [e for e in input_data.iterdir() if e.is_dir()]
    for line in TOData:
        input_data = Path(input_data, line)
        print(input_data)
        ckpt_name = 'checkpoint'
        #parser.add_option("-b", "--TOPath", dest="TOPath", default = '/data2/madhvi/Modeling/fluorescent_response_model/RCA_Docker_test/Assay2A-RU-OV-007-BL/',
        #                 help="set path to brightfield, fluorescent and checkpoint data")


        #(opt, args) = parser.parse_args()
        #preprocess and enhance contrast
        
        PreprocessData(input_data)
        print('Preprocessing data')
        #call inference to get the viability predictions as well as the fluorescence readouts 
        Inference(input_data, ckpt_name)
            
    
