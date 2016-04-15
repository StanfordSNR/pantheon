import os, sys, subprocess
import unittest

def generate_file():
    # generate a 1M file for now
    file_path = './test/test_files/random_input'
    if not os.path.isfile(file_path):
        with open(file_path, 'w') as f:
            f.write(os.urandom(1024 * 1024))
    
def main():
    generate_file() 

if __name__ == '__main__':
    main()
