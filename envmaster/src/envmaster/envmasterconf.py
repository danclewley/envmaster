"""
This file contains all the configuration variables
for the EnvMaster package. 
Only change these values if you know what you are doing.
"""

import sys

# Names of 'system' environment variables used
#==============================================
# for executeables
PATH = 'PATH'

# if there is a 64 bit version of 
# LD_LIBRARY_PATH use it
# only makes sense on some platforms
USE_64_LD_PATH_IF_AVAIL = True

# for libraries
if sys.platform == 'cygwin' or sys.platform == 'win32':
    LIBPATH = 'PATH'
elif USE_64_LD_PATH_IF_AVAIL and sys.platform == 'sunos5':
    LIBPATH = 'LD_LIBRARY_PATH_64'
elif USE_64_LD_PATH_IF_AVAIL and sys.platform == 'irix6-64':
    LIBPATH = 'LD_LIBRARY64_PATH'
elif sys.platform == 'darwin':
    LIBPATH = 'DYLD_LIBRARY_PATH'
else:
    LIBPATH = 'LD_LIBRARY_PATH'
# for man files
MANPATH = 'MANPATH'
# for python modules
PYPATH = 'PYTHONPATH'

# Subdirectories used relative to rootpath specified
# in setAll method
#==============================================

SUBDIRS = {'BIN_SUBPATH':['bin'],# for executeable files
            'LIB_SUBPATH':['lib'],# for libraries
            'INCLUDE_SUBPATH':['include'],# for include files
            'MAN_SUBPATH':['share/man','man'],# for man pages - tries 2 places
            # for python modules - this is where setup.py install --prefix
            # puts the files under the dir specified.
            'PYTHON_SUBPATH':['lib/python%d.%d/site-packages' % (sys.version_info[0],sys.version_info[1])]}
        
# Standard environment variable names
#==============================================
# name of module prepended onto these
# for 'bin' files
ENVNAMES = {'BIN_SUFFIX':'BIN_PATH',   # for 'bin' files
            'LIB_SUFFIX':'LIB_PATH', # for 'lib' files
            'INCLUDE_SUFFIX':'INCLUDE_PATH', # for 'include' files
            'MAN_SUFFIX':'MAN_PATH', # for man pages
            'PYTHON_SUFFIX':'PYTHON_PATH', # for python modules
            'ROOT_SUFFIX':'ROOT' # for root of package
            }

# Other EnvMaster internal settings
#==============================================
# environment variable used to keep track
# of which modules currently loaded
LOADEDMODULESENV = 'LOADEDENVMASTER'

# name of environment variable that contains
# all directories to look for modules under
ENVMASTERPATH = 'ENVMASTERPATH'

# list of directories to look in before those in ENVMASTERPATH
DEFAULTENVMASTERPATHS = []

# if multiple version of a module exist in a subdir
# uses this file to determine which one is default.
VERSIONFILE = 'version.py'
# Bit of Python in VERSIONFILE must set this Python
# variable
VERSIONVAR = 'version'

# All module files must start with this string or 
# they are ignored
ENVMASTERSENTINEL = '#%EnvMaster1.0'

# by default output for the shell is sent
# to stdout, and output for user sent to 
# stderr. Override by  changing these vars.
STDOUT = sys.stdout
STDERR = sys.stderr
