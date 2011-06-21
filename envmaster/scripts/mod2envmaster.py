#!/usr/bin/env python

"""
Script to assist converting old style module files to
EnvMaster files. Will do individual file, or convert
a whole tree, creating a new tree with directories 
matching the old tree as it goes. 
Gives module files the same name, but handles the
rename of the .version -> version.py file.
"""

import os
import sys
from envmaster import envmasterconf
from envmaster import envmasterexceptions

OLDFILESENTINEL = '#%Module1.0'
OLDVERSENTINEL = '#%Module'

_envre = None

def removeTCLenv(value):
    """
    Replaces all instances of '$env(BOB)' with '$BOB'
    as per EnvMaster standard. Code mainly stolen from
    os.path.expandvars() which does something similar.
    """
    global _envre
    if _envre is None:
        import re
        _envre = re.compile(r'\$env\(\w+\)')
    i = 0
    while True:
        m = _envre.search(value,i)
        if not m:
            break
        i, j = m.span(0)
        name = m.group(0)
        tail = value[j:]
        value = value[:i] + '$' + name[5:-1]
        i = len(value)
        value += tail
    return value
    
def getVarValue(line):
    """
    For a line that contains 'command var value'
    extract the var and value and run removeTCLenv()
    over them
    """
    # split the line on spaces
    arr = line.strip().split()
    # second item is the variable name
    var = arr[1]
    # sometimes the variable name looks 
    # up an environment varaible
    var = removeTCLenv(var)
    # the value can be quoted and because
    # we split on spaces and the may be embedded
    # spaces we join everything back together
    # I tried shlex but the plays with backslashes.
    value = ' '.join(arr[2:])
    value = removeTCLenv(value)
    # if it was quoted remove the quotes
    # as we usually add ours when we write the Python
    if value[0] == '"' or value[0] == "'":
        value = value[1:]
    if value[-1] == '"' or value[-1] == "'":
        value = value[:-1]
    return (var,value)
    

def mod2envmaster(old,new):
    """
    Does the conversion. Works out if it is a
    module file or version file and calls the
    appropriate function.
    """
    if os.path.basename(old) == '.version':
        modversion2envmaster(old,new)
    else:
        modfile2envmaster(old,new)

def modversion2envmaster(old,new):
    """
    Handles the conversion of a version file
    from old style to EnvMaster format.
    """
    fileobj = open(new,'w')
    count = 0
    for line in open(old):
        if count == 0:
            # check that it starts with the old style sentinel
            if not line.startswith(OLDVERSENTINEL):
                msg = '%s does not appear to be valid old version file' % old
                fileobj.close()
                os.remove(new)
                raise envmasterexceptions.EnvMasterParseError(msg)
            # write the new style one
            fileobj.write(envmasterconf.ENVMASTERSENTINEL + '\n')
        else:
            if line.startswith('#') or line.strip() == '':
                # comment or blank line - just copy
                fileobj.write(line)
            elif line.startswith('set ModulesVersion '):
                # this is the line that sets the TCL variable. 
                # replace with Python code in the new file
                version = line.strip().split()[-1]
                # sometimes this was in quotes, sometimes not.
                # we remove them to make it consistant and 
                # add our own.
                version = version.replace('"','')
                version = version.replace("'",'')
                fileobj.write('%s = "%s"\n' % (envmasterconf.VERSIONVAR,version))
            else:
                # can't really handle anything else ie TCL statements
                # so bail
                msg = 'Unable to convert line "%s" in file %s' % (line,old)
                fileobj.close()
                os.remove(new)
                raise envmasterexceptions.EnvMasterParseError(msg)
        count += 1
    fileobj.close()
    

def modfile2envmaster(old,new):
    """
    Convert a module file from old style to EnvMaster format.
    """
    # If the module conforms to the new athena convention
    # we should be able to do a better job of conversion and
    # make better use of setAll() etc. If we can determine the
    # 'package name' then we fill these vars in. Otherwise they 
    # stay None
    pkgname = None
    pkgroot= None
    fileobj = open(new,'w')
    count = 0
    for line in open(old):
        if count == 0:
            # check that it starts with the old style sentinel
            if not line.startswith(OLDFILESENTINEL):
                msg = '%s does not appear to be valid old module' % old
                fileobj.close()
                os.remove(new)
                raise envmasterexceptions.EnvMasterParseError(msg)
            # write the new style one
            fileobj.write(envmasterconf.ENVMASTERSENTINEL + '\n')
        else:
            if line.startswith('#') or line.strip() == '':
                # comment or blank line - just copy
                fileobj.write(line)
            elif line.startswith('module-whatis '):
                # a module-whatis
                arr = line.split()
                fileobj.write('module.whatis(%s)\n' % ' '.join(arr[1:]))
            elif line.startswith('prereq '):
                # a list of modules, one of which
                # must be loaded
                arr = line.split()[1:]
                s = ','.join(['"%s"' % mod for mod in arr])
                fileobj.write('module.prereq(%s)\n' % s)
            elif line.startswith('conflict '):
                # a list of modules, none of which
                # must be loaded
                arr = line.split()[1:]
                s = ','.join(['"%s"' % mod for mod in arr])
                fileobj.write('module.conflict(%s)\n' % s)
            elif line.startswith('module load '):
                # loading other modules
                arr = line.split()[2:]
                s = ','.join(['"%s"' % mod for mod in arr])
                fileobj.write('module.load(%s)\n' % s)
            elif line.startswith('module swap '):
                # module swap
                arr = line.split()[2:]
                s = ','.join(['"%s"' % mod for mod in arr])
                fileobj.write('module.swap(%s)\n' % s)
                
            elif line.startswith('setenv '):
                # a setenv command. See if we can do something clever
                # with setAll()
                (var,path) = getVarValue(line)
                emitsimple = True # default to just echoing same setVar
                if var.endswith('_' + envmasterconf.ROOT_SUFFIX):
                    # OK there is a variable that ends in _ROOT. Normally
                    # starts with the package name. Grab this and should
                    # be able to use setAll() for most things
                    oldfullpath = os.path.abspath(old)
                    possmodnames = [x.upper() for x in oldfullpath.split('/')[-2:]]
                    testpkgname = var.split('_')[0]
                    if testpkgname in possmodnames:
                        pkgname = testpkgname
                        pkgroot = pkgname + '_' + envmasterconf.ENVNAMES['ROOT_SUFFIX']
                    fileobj.write('module.setAll("%s")\n' % path)
                    emitsimple = False # don't emit anything else
                elif pkgname and var.startswith(pkgname):
                    # does it look like something that would have been
                    # set with setAll()?
                    handled = True
                    suffixes = [envmasterconf.ENVNAMES['BIN_SUFFIX'],envmasterconf.ENVNAMES['LIB_SUFFIX'],envmasterconf.ENVNAMES['INCLUDE_SUFFIX'],envmasterconf.ENVNAMES['MAN_SUFFIX'],envmasterconf.ENVNAMES['PYTHON_SUFFIX']]
                    for suffix in suffixes:
                        if not var.endswith('_' + suffix):
                            handled = False
                            break
                    if handled:
                        emitsimple = False
                        
                if emitsimple:
                    fileobj.write('module.setVar("%s","%s")\n' % (path,var))
                    
            elif line.startswith('set '):
                # TCL local variable
                # don't really have an equivalent - don't want to be 
                # stuffing around with Python variables
                # workaround - promote to environment variable
                (var,path) = getVarValue(line)
                fileobj.write('module.setVar("%s","%s")\n' % (path,var))

            elif line.startswith('prepend-path '):
                # a prepend-path command. See if we can do something clever
                # if a setAll() has been emited (pkgname will not be None)
                (var,path) = getVarValue(line)
                emitsimple = True
                
                # these are the likely paths that we can ignore as they 
                # are not constructed by setAll()
                if pkgname:
                    handled = True
                    ignorevars = [envmasterconf.PATH,envmasterconf.LIBPATH,envmasterconf.MANPATH,envmasterconf.MANPATH,envmasterconf.PYPATH]
                    ignoresubpaths = [envmasterconf.SUBDIRS['BIN_SUBPATH'][0],encmasterconf.SUBDIRS['LIB_SUBPATH'][0],envmasterconf.SUBDIRS['MAN_SUBPATH'][0],envmasterconf.SUBDIRS['MAN_SUBPATH'][1],envmasterconf.SUBDIRS['PYTHON_SUBPATH'][0]]
                    for (pathvar,subpath) in zip(ignorevars,ignoresubpaths):
                        likelypath = '$' + pkgroot + os.sep + pathvar
                        if var != pathvar or path != likelypath:
                            handled = False
                            break
                            
                    if handled:
                        emitsimple = False
                        
                if emitsimple:
                    fileobj.write('module.setPath("%s","%s")\n' % (path,var))
                
            else:
                # can't really handle anything else ie TCL statements
                # so bail
                msg = 'Unable to convert line "%s" in file %s' % (line.strip(),old)
                fileobj.close()
                os.remove(new)
                raise envmasterexceptions.EnvMasterParseError(msg)
                    
               
        
        count += 1
    fileobj.close()

if __name__ == '__main__':
    from optparse import OptionParser
    class CmdArgs:
        def __init__(self):
            self.parser = OptionParser()
            self.parser.add_option("--infile",dest="infile",default=None,help="Old style module file")
            self.parser.add_option("--outfile",dest="outfile",default=None,help="Output EnvMaster file")
            self.parser.add_option("--intree",dest="intree",default=None,help="Base of tree to scan for old style module files")
            self.parser.add_option("--outtree",dest="outtree",default=None,help="Base of tree to create EnvMaster files")
            self.parser.add_option("--keepgoing",dest="keepgoing",default=False,action="store_true",help="Ignore errors")
            (options, args) = self.parser.parse_args()
            for k in list(options.__dict__.keys()):
                self.__dict__[k] = options.__dict__[k]
    cmdargs = CmdArgs()
    
    if (cmdargs.infile is not None) != (cmdargs.outfile is not None):
        cmdargs.parser.print_help()
        raise SystemExit("If using --infile and --outfile, must specify both")
    elif (cmdargs.intree is not None) != (cmdargs.outtree is not None):
        cmdargs.parser.print_help()
        raise SystemExit("If using --intree and --outtree, must specify both")
    elif (cmdargs.infile is not None) == (cmdargs.intree is not None):
        cmdargs.parser.print_help()
        raise SystemExit("Use --infile/--outfile or --intree/--outree. Not both")
        
    if cmdargs.infile is not None and cmdargs.outfile is not None:
        mod2envmaster(cmdargs.infile,cmdargs.outfile)
    elif cmdargs.intree is not None and cmdargs.outtree is not None:
        intree = os.path.abspath(cmdargs.intree)
        outtree = os.path.abspath(cmdargs.outtree)
        for root, dirs, files in os.walk(intree):
            for filename in files:
                old = os.path.join(root,filename)
                newdir = outtree + root[len(outtree):]
                if filename == '.version':
                    new = os.path.join(newdir,envmasterconf.VERSIONFILE)
                else:
                    new = os.path.join(newdir,filename)
                print(old, new)
                if not os.path.isdir(newdir):
                    os.makedirs(newdir)
                    
                if cmdargs.keepgoing:
                    try:
                        mod2envmaster(old,new)
                    except envmasterexceptions.EnvMasterException as e:
                        print(e)
                else:
                    mod2envmaster(old,new)
    
