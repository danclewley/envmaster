#!/usr/bin/env python

"""
This module contains the EnvMasterEnv class
that executes module files and also 
represents the 'module' instance in executed
modules.
"""

import os
#from .envmasterfile import EnvMasterFile
from . import envmasterconf
from . import envmasterexceptions
from . import envmastershells

def modname2pkgname(modname):
    """
    Helper function to convert a module name
    (with optional version) into a package name
    which is the name of the module (without version)
    in upper case which is then used as a prefix
    for environment variables that are created.
    """
    pkgname = modname.split(os.sep)[0]
    return pkgname.upper()
    
class EnvMasterEnv(object):
    def __init__(self,shell,modname):
        self.modname = modname
        self.pkgname = modname2pkgname(modname)
        self.shell = shell
        # work out if we are just displaying
        # some operations are different
        self.isdisplay = isinstance(shell,envmastershells.DisplayShell)
        
        # add this module to the list of currently
        # loaded modules.
        # Don't bother doing this if we are in display
        # mode as will only confuse people.
        if not self.isdisplay:
            self.setPath(modname,envmasterconf.LOADEDMODULESENV)
        
    def makeVarName(self,suffix):
        """
        Given an environment variable 'suffix'
        prepend the name of the package. 
        This way all the variables start with the
        package name and look nice and tidy.
        """
        return '_'.join([self.pkgname,suffix])
        
    @staticmethod
    def dirHasFiles(path):
        """
        Check the specified directory exists, and
        contains some files (not just a subdir).
        Could do something more fancy liking checking
        files are exectuable for bin path etc, but far
        too hard right now...
        """
        dirok = os.path.isdir(path)
        if dirok:
            filecount = 0
            filelist = os.listdir(path)
            for fname in filelist:
                fullpath = os.path.join(path,fname)
                if os.path.isfile(fullpath):
                    filecount += 1
            dirok = filecount > 0
        return dirok
        
    @staticmethod
    def dirHasSubdirsOrFiles(path):
        """
        Similar to dirHasFiles but checks that dir
        has subdirectories as well as files. The 
        Python subdirs for instance often have
        just a subdir rather than files.
        """
        dirok = os.path.isdir(path)
        if dirok:
            filelist = os.listdir(path)
            dirok = len(filelist) > 0
        return dirok
        
    def setAll(self,rootpath):
        """
        Given the root path of a package attempt
        to fill as many variables as possible by
        testing the existance of subdirs with dirHasFiles()
        """
        # expand any environment vars in the path
        rootpath = os.path.expandvars(rootpath)
        if not os.path.isdir(rootpath):
            raise envmasterexceptions.EnvMasterPathException("Can't find %s" % rootpath)
    
        # the $PKG_ROOT var
        self.setVar(rootpath,self.makeVarName(envmasterconf.ENVNAMES['ROOT_SUFFIX']))
        
        # is there a bin directory?
        for subdir in envmasterconf.SUBDIRS['BIN_SUBPATH']:
            binpath = os.path.join(rootpath,subdir)
            if self.dirHasFiles(binpath):
                self.setBin(binpath)
                break
        
        # is there a lib directory?
        for subdir in envmasterconf.SUBDIRS['LIB_SUBPATH']:
            libpath = os.path.join(rootpath,subdir)
            if self.dirHasFiles(libpath):
                self.setLib(libpath)
                break

        # is there an include directory?
        # sometimes just a subdir
        for subdir in envmasterconf.SUBDIRS['INCLUDE_SUBPATH']:
            incpath = os.path.join(rootpath,subdir)
            if self.dirHasSubdirsOrFiles(incpath):
                self.setInclude(incpath)
                break

        # try for man path
        for subdir in envmasterconf.SUBDIRS['MAN_SUBPATH']:
            manpath = os.path.join(rootpath,subdir)
            if self.dirHasSubdirsOrFiles(manpath):
                self.setMan(manpath)
                break

        # python module subdirectory
        # - just check the existance of subdirs
        # - sometimes no files.
        for subdir in envmasterconf.SUBDIRS['PYTHON_SUBPATH']:
            pypath = os.path.join(rootpath,subdir)
            if self.dirHasSubdirsOrFiles(pypath):
                self.setPython(pypath)

    def setBin(self,path,var=envmasterconf.PATH):
        """
        Set the 'binary' directory into the PATH variable. 
        Also sets the BIN_SUFFIX variable so you can refer
        to this package's bin dir elsewhere
        """
        varname = self.makeVarName(envmasterconf.ENVNAMES['BIN_SUFFIX'])
        self.setVar(path,varname)
        self.setPath(path,var)

    def setLib(self,path,var=envmasterconf.LIBPATH):
        """
        Set the 'library' directory into the LIBPATH variable. 
        Also sets the LIB_SUFFIX variable so you can refer
        to this package's lib dir elsewhere
        """
        varname = self.makeVarName(envmasterconf.ENVNAMES['LIB_SUFFIX'])
        self.setVar(path,varname)
        self.setPath(path,var)

    def setMan(self,path,var=envmasterconf.MANPATH):
        """
        Set the 'man' directory into the MANPATH variable. 
        Also sets the MAN_SUFFIX variable so you can refer
        to this package's man dir elsewhere
        """
        varname = self.makeVarName(envmasterconf.ENVNAMES['MAN_SUFFIX'])
        self.setVar(path,varname)
        self.setPath(path,var)

    def setInclude(self,path):
        """
        Sets the INCLUDE_SUFFIX variable so you can refer
        to this package's include dir elsewhere
        """
        varname = self.makeVarName(envmasterconf.ENVNAMES['INCLUDE_SUFFIX'])
        self.setVar(path,varname)

    def setPython(self,path,var=envmasterconf.PYPATH):
        """
        Set the 'python' directory into the PYPATH variable. 
        Also sets the PYTHON_SUFFIX variable so you can refer
        to this package's python dir elsewhere
        """
        varname = self.makeVarName(envmasterconf.ENVNAMES['PYTHON_SUFFIX'])
        self.setVar(path,varname)
        self.setPath(path,var)
        
    def load(self,*modnames):
        """
        Load the specified modules. This get a bit circular
        here because we create another EnvMasterFile instance
        to process the modules, and a EnvMasterFile would
        have started the current load, but I think it is ok
        because it is a seperate transaction.
        """
        modfile = EnvMasterFile()
        modfile.runModule(self.shell,modnames,True)
        
    def swap(self,old,new):
        """
        unload 'old' and then load 'new'
        """
        modfile = EnvMasterFile()
        modfile.runModule(self.shell,[old],False)
        modfile.runModule(self.shell,[new],True)
        
    def prereq(self,*modnames):
        """
        Checks that at least one of the specified module(s) are loaded
        """
        if self.isdisplay:
            # don't do anything - just display it
            self.shell.setPrereq(modnames)
        else:
            modfile = EnvMasterFile()
            for mod in modnames:
                fullmod, fullpath = modfile.getModule(mod)
                if modfile.isLoaded(fullmod):
                    return
            # go to here so didn't find any modules already
            # loaded
            msg = 'None of the specified prerequisites (%s) required for package %s are loaded'
            msg = msg % (','.join(modnames),self.modname)
            raise envmasterexceptions.EnvMasterPrereqFailed(msg)
            

    def conflict(self,*modnames):
        """
        Checks that none of the specified module(s) are loaded
        """
        if self.isdisplay:
            # don't do anything - just display it
            self.shell.setConflict(modnames)
        else:
            modfile = EnvMasterFile()
            for mod in modnames:
                fullmod, fullpath = modfile.getModule(mod)
                if modfile.isLoaded(fullmod):
                    msg = 'Module %s already loaded which is listed as a conflict for package %s'
                    msg = msg % (mod,self.modname)
                    raise envmasterexceptions.EnvMasterConflictFailed(msg)
                    
    def whatis(self,desc):
        """
        Sets the desciption of the module. Only used in 
        display mode.
        """
        if self.isdisplay:
            self.shell.setWhatIs(desc)
                

    def setVar(self,value,var,addpkgname=False):
        """
        Gets the current shell object to set the 
        environment variable 'var' to the value 
        specified. If addpkgname is True it prepends
        the name of the package to the variable name
        like the setBin() etc methods do.
        """
        # expand any embedded environment vars
        value = os.path.expandvars(value)
        if addpkgname:
            var = self.makeVarName(var)
        self.shell.setVar(value,var)

    def setPath(self,path,var):
        """
        Gets the current shell object to prepend
        'path' onto the existing environment variable
        'var'. 
        """
        # expand any embedded environment vars
        path = os.path.expandvars(path)
        self.shell.setPath(path,var)
            
    def execute(self,path):
        """
        Execute the module specified. 'path' must
        contain full path to the actual module file
        as returned by EnvMasterFile.getModule()
        """
        global_ns = {}
        # set the 'module' variable to this object
        global_ns['module'] = self
        # get Python to execute it
        exec(compile(open(path).read(), path, 'exec'),global_ns,global_ns)
            

