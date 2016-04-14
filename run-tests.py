import os, sys

def generate_large_file():
    if not os.path.isfile('./test/test-files/random-input'):
        with open('./test/test-files/random-input', 'w') as f:
            f.write(os.urandom(1024 * 1024))
    
def main():
    generate_large_file() 
    print "Test run-tests.py" 

if __name__ == '__main__':
    main()
