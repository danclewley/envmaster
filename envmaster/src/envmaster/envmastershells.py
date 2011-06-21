"""
This module contains the 'shells'. These are classes
that generate commands for the shell (bash,csh etc)
they represent. 

Generally, the setVar() and setPath() commands are
used on an instance. They store the commands. To 
write all the commands out use flush().

Normally, instances of these classes are not created
directly. Use the shellFromString() method.
"""

import os
import sys
from . import envmasterformat
from . import envmasterconf

def shellFromString(shellname,loading):
    """
    Returns an appropriate Shell instance for the
    name of the shell pass in 'shellname'. The 'loading'
    parameter determines is a module is being loaded
    or unloaded.
    """
    shellname = shellname.lower()
    if shellname == "bash":
        shell = BashShell(loading)
    elif shellname == "disp":
        shell = DisplayShell(loading)
    elif shellname == "csh" or shellname == 'tcsh':
        shell = CShell(loading)
    elif shellname == "python":
        shell = PythonShell(loading)
    elif shellname == "pythonsilent":
        shell = PythonSilentShell(loading)
    elif shellname == "r":
        shell = RShell(loading)
    elif shellname == "bob":
        shell = BobShell(loading)
    else:
        raise ValueError("Unknown shell %s" % shellname)

    return shell

class BaseShell(object):
    """
    The base class that all shells derive from.
    """
    def __init__(self,loading):
        """
        The constructor. Derived class should call this.
        Takes whether module being loaded or unloaded.
        """
        self.loading = loading
        # dictionary of commands keyed on variable name
        # we do this so only one command gets executed per
        # variable name. We know that the last one should 
        # incorporate all the others because of the way we 
        # have updated the environment of the current 
        # process with each change.
        self.cmds = {}
        
    def addCmd(self,cmd,var):
        """
        Adds a command to the buffer of commands to be
        given to the shell. Derived class should call 
        this for each command they add.
        """
        self.cmds[var] = cmd
        
    def findFullPath(self,path,var):
        """
        Derived classes should call this in their setPath()
        methods. This finds what the full value of the path
        variable should be - ie with the existing paths intact
        and the new one added or removed.
        """
        fullpath = None

        if self.loading:
            oldval = os.getenv(var)
            if oldval is None or oldval == '':
                # first value to be added to this path var
                fullpath = path
            else:
                # prepend this path to the existing.
                arr = oldval.split(os.pathsep)
                arr.insert(0,path)
                fullpath = os.pathsep.join(arr)
            
        else:
            # unloading
            oldval = os.getenv(var)
            if oldval is not None or oldval != '':
                # remove this path from the path var
                arr = oldval.split(os.pathsep)
                try:
                    arr.remove(path)
                except ValueError:
                    # shouldn't happen but if it does
                    # just ignore
                    pass
                fullpath = os.pathsep.join(arr)
            else:
                # hadn't been set. Weird?
                fullpath = ''
        return fullpath
        
    def setVar(self,value,var):
        """
        Base class implementation. Just updates the
        environment for the current Python process
        ie not communicated with the shell.
        We do this so that:
        1) os.expandvars works as expected for
            any other operations we do
        2) other modules being loaded that check
            for this var behave as expected
        All derived implementations should call this.
        """
        if self.loading:
            os.environ[var] = value
        elif var in os.environ:
            del os.environ[var]

    def setPath(self,fullpath,var):
        """
        Base class implementation. Just updates the
        environment for the current Python process
        ie not communicated with the shell.
        We do this so that:
        1) findFullPath() behaves properly for any
            other modules being loaded as preserves
            the path just added.
        All derived implementations should call this.
        """
        os.environ[var] = fullpath
    
    def flush(self):
        """
        Writes the buffered commands out to the shell.
        Derived classes reimplement if they need to 
        do something different.
        """
        for var in sorted(self.cmds.keys()):
            envmasterconf.STDOUT.write(self.cmds[var] + '\n')
        self.cmds = []

class DisplayShell(BaseShell):
    """
    Class that prepares commands for display to the screen.
    ie doesn't actually echo stuff to the shell. 
    """
    def __init__(self,loading):
        super(DisplayShell,self).__init__(loading)
        self.modname = None
        self.cmdtable = [] # table of commands for display
        
    def setModName(self,modname):
        """
        If this is called will display the modname
        as part of the output.
        """
        self.modname = modname        

    def setVar(self,value,var):
        """
        Set an environment variable. Here we don't actually
        use self.addCmds but accumulate our table in 
        self.cmdtable and display using envmasterformat
        """
        self.cmdtable.append('setenv')
        self.cmdtable.append(var)
        self.cmdtable.append(value)
        super(DisplayShell,self).setVar(value,var)
        
    
    def setPath(self,value,var):
        """
        Set a path variable. Here we don't actually
        use self.addCmds but accumulate our table in 
        self.cmdtable and display using envmasterformat
        """
        self.cmdtable.append('prepend-path')
        self.cmdtable.append(var)
        self.cmdtable.append(value)
        # we don't call the base class as we don't
        # call findFullPath. Not sure this is correct...
        
    def setPrereq(self,modnames):
        """
        Log that the module needs one of specifed prereq
        modules
        """
        self.cmdtable.append('prereq')
        self.cmdtable.append('')
        self.cmdtable.append(' '.join(modnames))

    def setConflict(self,modnames):
        """
        Log that the module needs none specifed 
        modules loaded before it can load
        """
        self.cmdtable.append('conflict')
        self.cmdtable.append('')
        self.cmdtable.append(' '.join(modnames))
        
    def setWhatIs(self,desc):
        """
        Log the description of the module
        """
        self.cmdtable.append('whatis')
        self.cmdtable.append('')
        self.cmdtable.append(desc)
        
    def flush(self):
        """
        Reimplementation of base class method to
        format our table using envmasterformat.displayTable()
        """
        format = envmasterformat.EnvMasterFormat()
        # if we got given a modname display it
        if self.modname is not None:
            format.displayTitle(self.modname)
        # ours is a 3 column table
        format.displayTable(self.cmdtable,3)
        self.cmdtable = []

class BashShell(BaseShell):
    """
    Derived class to support the bash shell
    """
    def __init__(self,loading):
        super(BashShell,self).__init__(loading)
    
    def setVar(self,value,var):
        """
        Creates commands in bash format for 
        setting/unsetting variables.        
        """
        if self.loading:
            self.addCmd('%s="%s" ;export %s;' % (var,value,var),var)
        else:
            self.addCmd('unset %s; ' % (var),var)
        super(BashShell,self).setVar(value,var)

    def setPath(self,value,var):
        """
        Creates command in bash format for setting
        the new path
        """
        fullpath = self.findFullPath(value,var)
        self.addCmd('%s="%s" ;export %s;' % (var,fullpath,var),var)
        super(BashShell,self).setPath(fullpath,var)

class CShell(BaseShell):
    """
    Derived class to support the C-shell and tcsh
    """
    def __init__(self,loading):
        super(CShell,self).__init__(loading)
    
    def setVar(self,value,var):
        """
        Creates commands in csh format for 
        setting/unsetting variables.        
        """
        if self.loading:
            self.addCmd('setenv %s "%s"; ' % (var,value),var)
        else:
            self.addCmd('unsetenv %s; ' % (var),var)
        super(CShell,self).setVar(value,var)

    def setPath(self,value,var):
        """
        Creates command in csh format for setting
        the new path
        """
        fullpath = self.findFullPath(value,var)
        self.addCmd('setenv %s "%s"; ' % (var,fullpath),var)
        super(CShell,self).setPath(fullpath,var)

class BobShell(BaseShell):
    """
    Ahh the lesser known bob shell. My personal 
    favourite due to its brief but expressive 
    syntax.
    """
    def __init__(self,loading):
        super(BobShell,self).__init__(loading)
    
    def setVar(self,value,var):
        """
        Creates commands in bob format for 
        setting/unsetting variables.        
        """
        if self.loading:
            self.addCmd('bob bob%s "%s"\n' % (var,value),var)
        else:
            self.addCmd('unbob %s\n' % (var),var)
        super(BobShell,self).setVar(value,var)

    def setPath(self,value,var):
        """
        Creates command in bob format for setting
        the new path
        """
        fullpath = self.findFullPath(value,var)
        self.addCmd('bob bob%s "%s"\n' % (var,fullpath),var)
        super(BashShell,self).setPath(fullpath,var)

class PythonShell(BaseShell):
    """
    Derived class to support Python.
    Actually one wouldn't use this to load a module
    since it wouild be better to have the vars set in
    the current Python process. Use BlankShell()
    """
    def __init__(self,loading):
        super(PythonShell,self).__init__(loading)
    
    def setVar(self,value,var):
        """
        Creates commands in Python format for 
        setting/unsetting variables.        
        """
        if self.loading:
            self.addCmd("os.environ['%s'] = '%s')\n" % (var,value),var)
        else:
            self.addCmd("os.unsetenv('%s')\n" % (var),var)
        super(PythonShell,self).setVar(value,var)

    def setPath(self,value,var):
        """
        Creates command in Python format for setting
        the new path
        """
        fullpath = self.findFullPath(value,var)
        self.addCmd("os.setenv('%s','%s')\n" % (var,fullpath),var)
        super(BashShell,self).setPath(fullpath,var)

class PythonSilentShell(BaseShell):
    """
    Derived class to support loading modules into the
    current Python process. Just uses the base classes
    implementation of setVar and setPath that just 
    sets the variables into the current environment.
    """
    def __init__(self,loading):
        super(PythonSilentShell,self).__init__(loading)
        
    def setPath(self,value,var):
        if var == envmasterconf.PYPATH:
            # if it is the PYTHONPATH
            # it's not going to do much good changing the 
            # environment since sys.path already populated
            # when python starts. Better to update sys.path
            if self.loading:
                sys.path.append(value)
            else:
                try:
                    sys.path.remove(value)
                except ValueError:
                    pass
        fullpath = self.findFullPath(value,var)
        super(PythonSilentShell,self).setPath(fullpath,var)
    
    def flush(self):
        """
        Do nothing as we should have already changed the 
        environment of the current (Python) process.
        """
        pass

class RShell(BaseShell):
    """
    Derived class to support R
    """
    def __init__(self,loading):
        super(RShell,self).__init__(loading)
    
    def setVar(self,value,var):
        """
        Creates commands in R format for 
        setting/unsetting variables.        
        """
        if self.loading:
            self.addCmd('Sys.setenv(%s="%s")' % (var,value),var)
        else:
            self.addCmd('Sys.unsetenv("%s")' % (var),var)
        super(RShell,self).setVar(value,var)

    def setPath(self,value,var):
        """
        Creates command in R format for setting
        the new path
        """
        fullpath = self.findFullPath(value,var)
        self.addCmd('Sys.setenv(%s="%s")' % (var,fullpath),var)
        super(RShell,self).setPath(fullpath,var)
