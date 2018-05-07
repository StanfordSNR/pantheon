import os
from os import path
import sys
base_dir = path.abspath(path.join(path.dirname(__file__), os.pardir))
src_dir = path.join(base_dir, 'src')
sys.path.append(src_dir)
