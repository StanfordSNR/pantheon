import os
from os import path
import sys
project_root = path.abspath(path.join(path.dirname(__file__), os.pardir))
src_dir = path.join(project_root, 'src')
sys.path.append(src_dir)
