import sys
import os
from os import path
DIR = path.abspath(path.join(path.dirname(path.abspath(__file__)),
                             os.pardir, os.pardir))
sys.path.append(DIR)
