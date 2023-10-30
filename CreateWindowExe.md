# Installing a standalone on windows.

The standalone version of iSpector is a windows executable, that is not
dependent on having Python installed, if you have python installed it wont use
it.


# Recommendations to get iSpector to work.

The author uses git-bash to run python and all commands. I like to create
and activate a virtual environment. In order to install all dependencies.
So create the environment

## Installing dependencies using pip

Once you've activated the environment install the requirements:

```bash
pip install -r requirements.txt
```

## Create a stand alone python binary for windows

You'll first need to know that iSpector runs, before creating the executable.
You can test this by running iSpector.py.

For the next points you can make a "windowed" version of the program by adding
"--windowed" command line flag to pyinstaller. However, it is easier to build a
working command line version first because then you can easily start the program
in the command line and then you see the errors printed to stderr.

- install python python 3.x
- install pyinstaller with pip.
  go to the iSpector library and type `pyinstaller iSpector.spec`
  (for some errors see point three). The iSpector.spec file contains the
  python code in order to create a windows iSpector.exe executable file.
- It can be the case that some libraries are not found during runtime
  notably cython_blas and cython_lapack.
  --hidden-import="scipy.linalg.cython_blas"
  --hidden-import="scipy.linalg.cython_lapack"
  (this point might be out dated).
  Now it should run successfully.
- Optional: run pyinstaller with all flags as previously and add the --windowed
  flag to make a more typical windows program.

## Creating a windows installer

Install Nullsoft Scriptable Install System:
[https://sourceforge.net/projects/nsis/](NSIS):


After these steps have run successfully you have a standalone iSpector in the
dist folder. You need to run:

```bash
makensis iSpector-installer.nsi
```

This will create a windows installer.

Good luck!
