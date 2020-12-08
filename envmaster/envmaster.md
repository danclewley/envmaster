EnvMaster
----------


### 1 Introduction

This package is based on Modules
([http://modules.sourceforge.net/](http://modules.sourceforge.net/)).
Both Modules and EnvMaster allow packages to be installed in separate
directories from each other and ’loaded’ into the users environment on
demand. They also allow multiple versions of the same package to be
installed concurrently and a particular version loaded.

EnvMaster attempts to address some of the limitations of the original
design, not least its dependence on TCL. I have also tried to automate
some of the more repetitive aspects of creating modules.

### 2 Use

#### 2.1 Installation

First untar the distribution. It is usually wisest to install separate
from your Python distribution like this:

```
export ENVMASTER_ROOT=/opt/envmaster
python setup.py install --prefix=$ENVMASTER_ROOT
export PATH=$ENVMASTER_ROOT/bin:$PATH
export PYTHONPATH=$ENVMASTER_ROOT/lib/pythonX.X/site-packages:$PYTHONPATH
```

Where ’pythonX.X’ is the version of your Python distribution.
ENVMASTER_ROOT can be any directory you have write access to.

##### 2.1.1 Where Python isn’t available (or is an older version)

In the case where there is no Python available, and you need to load it
with EnvMaster, a ’frozen’ version of EnvMaster needs to be prepared.
More to come on this...

In the case where the system has an older version of Python available
(say 2.4) and you want to load a newer version using EnvMaster (say
2.6), some care is required for setting up paths. When you do the
install (as above) with the system python (2.4), the site packages
directory will be called $ENVMASTER_ROOT/lib/python2.4/site-packages.
This is fine when using the system Python. However, if you were to load
Python 2.6 with EnvMaster, it won’t be able to find it’s components
because it will be looking in
$ENVMASTER_ROOT/lib/python2.6/site-packages. The best workaround is to
create a link called $ENVMASTER_ROOT/lib/python2.6 pointing to
$ENVMASTER_ROOT/lib/python2.4. Also, it pays to check that distutils
hasn’t re-written the first line of envmastercmd.py.

On a related note, it is best to load the newer version of Python first
and separately from other Python packages, otherwise the wrong site
packages directory will be used.

#### 2.2 Initialisation

For tcsh users:
```
source $ENVMASTER_ROOT/init/tcsh
```

For bash users
```
source $ENVMASTER_ROOT/init/bash
```

For zsh users
```
source $ENVMASTER_ROOT/init/zsh
```

Your $ENVMASTERPATH variable needs to be set to the location of your
module files. See Section [3](#x1-80003).

#### 2.3 Commands

Once EnvMasters is initialised, the following commands will be
available:

```
envmaster list
```

Displays the currently loaded modules

```
envmaster avail
```

Displays all the modules that are available. Normally various versions
of each module are available. The default version is marked with
(default).

```
envmaster load module/version
```

Loads a module. If version not specified, default is used.

```
envmaster unload module/version
```

Unloads a currently loaded module

```
envmaster disp module/version
```

Displays what a module does (without loading it). If version not
specified, default is used.

```
envmaster swap module/version module/version
```

Switches between versions of a module.

#### 2.4 Calling from Python

```
from envmaster import pyutils
```

Currently there are 2 methods: pyutils.load() and pyutils.unload() which
take a single string with a module name, or a list.

### 3 How to write module files

The $ENVMASTERPATH variable must be set to a semi-colon separated list
of directories. Each of these directories is searched for EnvMaster
files. This is usually in a separate tree from the software
installation.

#### 3.1 Directory Layout

Files under each directory in $ENVMASTERPATH are treated as EnvMaster
files if the first line starts with `#%EnvMaster1.0`. There are two
sorts of EnvMaster files: versioned and unversioned. Unversioned files
sit at the root of the directory. A file here will show up as an
available module. Using this type is not recommended because the whole
idea of EnvMasters is to have multiple versions of software installed.
However in some instances there is only ever one version and this does
make sense.

The second type is a versioned EnvMaster file. These live in
subdirectories immediately below the root of the directory and these
directories usually have the same name as the software they load. They
are normally named to match the version of the software ie python/2.6.5.
There can be many of these files, one per version installed. The default
version is the first, or dictated by the version.py file if installed
(see below). If the version of the module to be loaded is not specified
by the user, it is this default version that is used. The user can of
course override this and specify a particular version they wish to use.

For example, for the directory layout below, there are 2 EnvMasters, one
called ’unversionedsw’ that is not versioned. The second (’python’) has
3 versions that can be chosen between.

```
$ENVMASTERPATH=/opt/modules
/opt/modules/unversionedsw
/opt/modules/python/2.5.1
/opt/modules/python/2.6.0
/opt/modules/python/2.6.5
```

#### 3.2 File contents

EnvMaster files are just fragments of Python so can contain any valid
Python statements. There are a number of functions meaningful in a
EnvMaster context. The following discusses the operations that are
performed for each function when a module is loaded. It is worth noting
the opposite is performed when modules are unloaded (ie variables unset
etc).

```python
module.setAll(path)
```

Searches the path given and sets the following variables in certain
conditions, where MODNAME is the name of the EnvMaster in capitals (ie
PYTHON)

* $MODNAME_ROOT is set to the root path specified
* If it exists and contains files, the ’bin’ subdirectory is added to the $PATH and put into the $MODNAME_BIN_PATH variable
* If it exists and contains files, the ’lib’ subdirectory is added to the $LD_LIBRARY_PATH (or whatever variable makes sense for the current OS) and put into the $MODNAME_LIB_PATH variable
* If it exists and contains files or sub directories, the ’include’ subdirectory is put into the $MODNAME_INCLUDE_PATH variable
* If either the ’man’ subdirectory or ’share/man’ subdirectory exists and contains files it is added to the $MANPATH and put into the $MODNAME_MAN_PATH variable.
* If the ’lib/pythonX.X/site-packages’ directory exists (where X.X is the version of Python EnvMaster is running) and contains files or subdirectories, then it is added to the $PYTHONPATH and put into the $MODNAME_PYTHON_PATH variable.

Normally, setAll() is the only method that needs to be called as it
handles most common situations. Other methods which can be added are:

```python
module.setBin(binpath)
```
Adds binpath to the $PATH and put into $MODNAME_BIN_PATH

```python
module.setLib(libpath)
```
Adds libpath to the $LD_LIBRARY_PATH (or whatever variable makes
sense for the current OS) and put into $MODNAME_LIB_PATH.

```python
module.setMan(manpath)
```
Adds manpath to the $MANPATH and put into $MODNAME_MAN_PATH

```python
module.setInclude(includepath)
```
Puts includepath into $MODNAME_INCLUDE_PATH

```python
module.setPython(pythonpath)
```
Adds pythonpath to $PYTHONPATH and put into $MODNAME_PYTHON_PATH

```python
module.load(modnames)
```
Load specified EnvMaster(s). Use of this function is not recommended as
it makes it difficult to manage dependencies. It is better to force the
user to load necessary EnvMasters themselves with the module.prereq
function.

```python
module.swap(old,new)
```
Unloads module given in old and replaces it with that contained in new.
See comments above on load().

```python
module.prereq(modnames)
```
Checks at least one of the specified modules is loaded. If you want to
check a number of modules is loaded, then call this function separately
once for each module. If the module isn’t loaded, an error is returned
to the user and nothing is loaded.

```python
module.conflict(modnames)
```
Raises an error if one of the specified modules is loaded.

```python
module.whatis(description)
```
Sets the description of the modules. This is only seen when doing a
’EnvMaster disp’

```python
module.setVar(value,varname,addpkgname=False)
```
Sets the environment variable named in varname to value. If addpkgname
is True, then MODNAME_ is prepended to the varname.

```python
module.setPath(path,varname)
```
Prepends path onto environment variable specified in varname. Designed
to use with $PATH and other environment variables that contain a list
of paths.

##### 3.2.1 Version files

If present, a file with the name of ’version.py’ in a versioned
EnvMasters directory is parsed to choose which version is the default.
This file needs to start with `#%EnvMaster1.0` and can contain any
number of Python statements. It need only contain one other line that
sets the Python variable ’version’ to a string containing the version
number that should be made the default. Here is an example:

```python
#%EnvMaster1.0

version = ’1.0.0’
```

##### 3.2.2 Installation guide

When configuring software, use the prefix option to install the software
in a uniquely versioned directory. For autoconf software:

```
./configure --prefix=/opt/python/2.6.5
```

For python software

```
python setup.py install --prefix=/opt/matplotlib/1.0.0
```

Then create a EnvMaster file to match

#### 3.3 mod2envmaster.py

Utility to ease transition from traditional modules to EnvMasters. More
to come...

#### 3.4 Configuration

The file
$ENVMASTER_ROOT/lib/pythonX.X/site-packages/EnvMaster/envmasterconf.py
contains a number of settings. Changing this file will allow you to
override almost any aspect of EnvMaster.
