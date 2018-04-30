import os
from os import path
import sys
src_dir = path.abspath(path.join(path.dirname(__file__), os.pardir))
third_party_dir = path.abspath(path.join(src_dir, os.pardir, 'third_party'))
sys.path.append(src_dir)
