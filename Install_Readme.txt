Install a standalone on windows.

Recommendations to get iSpector to work. This is mainly written for awful OS-es
that don't ship with apt-get or yum or equivalent to install all necessary
dependencies.

These modules must be installed
    - PyQt4     (Windows: just install a binary)
    - Pil       (Windows: install with pip our from binary)
    - SciPy     (Windows: install with a binary)
    - Numpy     (Windows: install with a binary)
    - Matplotlib(Windows: install with pip
    - PyCairo   (optional) You'll get a warning when it is not installed

    
To make a stand alone python binary for windows.
For the next points you can make a "windowed" version of the program by adding
"--windowed" command line flag to pyinstaller. However, it is easier to build a
working command line version first because then you can easily start the program
in the command line and then you see the errors printed to stderr.

0   install python (tested with 2.7.10) python 3.x won't work at the moment
1   install pyinstaller with pip.
2   go to the iSpector library and type `pyinstaller iSpector.py`
    (for some errors see point three)
3   edit under C:\Python27\Lib\site-packages\PyInstaller\hooks\" the files
    hook_PIL.py and hook-PIL.SpiderImagePlugin.py
    comment out the lines that start with #excludedimports
    now it should build but then during running the program you'll encounter
    errors related to point 4.
4   It can be the case that some libraries are not found during runtime
    notably cython_blas and cython_lapack. 
    --hidden-import="scipy.linalg.cython_blas"
    --hidden-import="scipy.linalg.cython_lapack"
5   Now it should run succesfully.
6   Optional: run pyinstaller with all flag and add the --windowed flag to make
    a more typical windows program.

After these steps have run successfully you have a standalone iSpector in the
dist folder. You need to run 'makensis iSpector-installer.nsi' This will
create a windows installer.

You are ready.
