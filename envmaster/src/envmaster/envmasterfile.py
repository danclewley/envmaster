#!/usr/bin/env python
"""
Handles the major module operations. envmastercmd.py
just calls through to this.
"""
import os
import envmasterconf
import envmasterexceptions
import envmasterformat
from envmastershells import shellFromString


class EnvMasterFile(object):
    """
    Class that knows where to look for module files
    and can perform the major module operations
    """
    def __init__(self):
        # construct our list of where to look for modules
        # copy the list in the conf file
        self.modpaths = envmasterconf.DEFAULTENVMASTERPATHS[:]
        # append the paths in the environment variable
        modpathenv = os.getenv(envmasterconf.ENVMASTERPATH)
        if modpathenv is not None:
            for path in modpathenv.split(os.pathsep):
                self.modpaths.append(path)
                
    def findDefault(self,dirpath):
        """
        Given a directory with one or more module files 
        in it looks for the version file and determines the
        fully qualififed (with version) module name.
        If no version file, just returns the first one.
        """
        defaultmodname = None
        # in case we were given a version
        modbase = dirpath.split(os.sep)[-1]
        
        # name of version file
        versionpath = os.path.join(dirpath,envmasterconf.VERSIONFILE)
        if os.path.exists(versionpath) and self.isEnvMasterFile(versionpath):
            localdict = {}
            # run Python over it
            exec(compile(open(versionpath).read(), versionpath, 'exec'),localdict,localdict)
            if envmasterconf.VERSIONVAR not in localdict:
                # didn't set the version variable
                msg = "Variable %s not set in file %s" 
                msg = msg % (envmasterconf.VERSIONVAR,versionpath)
                raise envmasterexceptions.EnvMasterParseError(msg)
                
            # now look for that version 
            defaultversion = localdict[envmasterconf.VERSIONVAR]
            defaultmodpath = os.path.join(dirpath,defaultversion)
            if not os.path.exists(defaultmodpath):
                msg = "Unable to find default module version %s"
                msg = msg % defaultversion
                print(dirpath)
                raise envmasterexceptions.EnvMasterPathException(msg)
                
            defaultmodname = modbase + os.sep + defaultversion
        else:
            # look for first one
            dirlisting = os.listdir(dirpath)
            if len(dirlisting) != 0:
                defaultmodname = modbase + os.sep + os.listdir(dirpath)[0]
            else:
                # no files - about all we can do
                defaultmodname = modbase
            
        return defaultmodname
                
    def getModule(self,modname):
        """
        Finds the default version of the module,
        and the actual full path to the module file
        """
        fullpath = None
        fullmodname = None
        # search all our paths for the module
        for path in self.modpaths:
            # test to see if we found it
            testpath = os.path.join(path,modname)
            if os.path.exists(testpath):
                if os.path.isdir(testpath):
                    # it's a dir so look for default version
                    fullmodname = self.findDefault(testpath)
                    fullpath = os.path.join(path,fullmodname)
                else:
                    # don't have to look any further
                    fullmodname = modname
                    fullpath = testpath
                break
                
        if fullpath is not None and not self.isEnvMasterFile(fullpath):
            msg = 'Module %s not EnvMaster' % fullpath
            raise envmasterexceptions.EnvMasterParseError(msg)
                
        return(fullmodname,fullpath)
        
    def isLoaded(self,fullmodname):
        """
        Given a full module name (ie with version) as
        returned by getModule() determine whether that 
        module is currently loaded
        """
        loaded = os.getenv(envmasterconf.LOADEDMODULESENV)
        if loaded is None:
            return False
        else:
            loaded = loaded.split(os.pathsep)
            return fullmodname in loaded
        
    def isEnvMasterFile(self,fullpath):
        """
        Checks the fill path to a EnvMaster module
        file and sees if it is a valid module
        file (has the sentinel)
        """
        sentinel = envmasterconf.ENVMASTERSENTINEL
        fileobj = open(fullpath)
        # just read the number of bytes we
        # need to check
        bufferstr = fileobj.read(len(sentinel))
        fileobj.close()
        return sentinel == bufferstr

    def runModule(self,shell,modlist,loading):
        """
        Execute the module files in modlist. Either in
        loading or unloading mode depending on the
        value of loading. Also takes the name of the
        shell to generate commands for.
        """
        # create the shell object for the type of shell
        # we are dealing with
        shell = shellFromString(shell,loading)

        # go thru each module    
        for modname in modlist:
        
            # get the full module name with version
            # plus path
            fullmod,path = self.getModule(modname)
            if fullmod is None:
                msg = "Can't find Module '%s'" % modname
                raise envmasterexceptions.EnvMasterNoModule(msg)
            # only run if loading and not already loaded
            # or unload only if loaded
            isloaded = self.isLoaded(fullmod)
            if (loading and not isloaded) or (not loading and isloaded):
                    # create the EnvMasterEnv object to do the running
                    env = EnvMasterEnv(shell,fullmod)
                    env.execute(path)
        # flush out all the commands
        shell.flush()
        
    def dispModule(self,modlist):
        """
        Displays what the modules do in modlist.
        Shows them in order.
        """
        # create an object for the display shell
        shell = shellFromString('disp',True)
    
        # go thru each module
        for modname in modlist:
            # get the full module name with version
            # plus path
            fullmod,path = self.getModule(modname)
            if fullmod is None:
                msg = "Can't find Module '%s'" % modname
                raise envmasterexceptions.EnvMasterNoModule(msg)
            # set the modname so that shell can display its
            # title
            shell.setModName(path)
            # create the EnvMasterEnv object and run it
            env = EnvMasterEnv(shell,fullmod)
            env.execute(path)
            shell.flush()
                
    def availModules(self):
        """
        Displays to the terminal a list of all the
        available modules
        """

        format = envmasterformat.EnvMasterFormat()
        
        totalmodules = 0

        # for each search directory
        for path in self.modpaths:
            availmodules = []
            format.displayTitle(path)
            # walk that directory looking for module files
            for root, dirs, files in os.walk(path):

                if root != path:
                    # we are in a subdir - find the 
                    # default module file so we can show
                    # which one is default
                    defaultmod = self.findDefault(root)

                # go thru all the module files in the dir
                for filename in files:
                    # ignore the version.py file
                    if filename != envmasterconf.VERSIONFILE:
                        fullpath = os.path.join(root,filename)
                        # is it a EnvMasterFile?
                        if self.isEnvMasterFile(fullpath):
                            modname = filename
                            if root != path:
                                # in a subdir
                                # create the module name from the dir name
                                modname = root.split(os.sep)[-1] + os.sep + filename
                                if defaultmod == modname:
                                    # is the default - add a note
                                    modname += '(default)'
                            availmodules.append(modname)
              
            # show the modules in sorted alphabetical order
            availmodules.sort()
            # show them
            format.listAsColumns(availmodules)
            
            totalmodules += len(availmodules)
            
        if totalmodules == 0:
            msg = "No module files found"
            raise envmasterexceptions.EnvMasterNoModules(msg)
            
    def listModules(self):
        """
        List the currently loaded modules to the screen.
        Uses envmasterformat to format it as it a multi column list
        """
        
        format = envmasterformat.EnvMasterFormat()
        format.displayTitle("Currently Loaded EnvMaster files")
        loaded = os.getenv(envmasterconf.LOADEDMODULESENV)
        if loaded is not None and loaded != '':
            loaded = loaded.split(os.pathsep)
            numbered = []
            count = 1
            # go thru each one and add a 
            # number to the start of it so its
            # easy to see which order they are in
            loaded.reverse()
            # display in reversed order so the first
            # one loaded is shown first
            for mod in loaded:
                disp = '%d) %s' % (count,mod)
                numbered.append(disp)
                count += 1
            format.listAsColumns(numbered)
        else:
            msg = 'No EnvMasters currently loaded'
            format.listAsColumns([msg])

# hack to avoid circular import problem                               
from envmasterenv import EnvMasterEnv

if __name__ == '__main__':
    

    
    f = EnvMasterFile()
    #f.availModules()
    f.dispModule(['lyx','qgis'])
    
