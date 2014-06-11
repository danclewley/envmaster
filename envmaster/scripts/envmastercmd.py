#!/usr/bin/env python
"""
Script that generates commands to be evaluated 
by the shell. These commands load or unload
modules. 
"""
# This file is part of EnvMaster
# Copyright (C) 2012  Sam Gillingham
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
import os
import sys
from envmaster import envmasterfile
from envmaster import envmasterformat

def printUsage():
    """
    Print a simple usage message
    and exit
    """
    fmt = envmasterformat.EnvMasterFormat()
    fmt.displayTitle("Usage")
    
    helplist = []
    
    helplist.extend(['Command','Option','Arguments','Help'])
    helplist.extend(['-------','------','---------','----'])
    helplist.extend(['envmaster','avail','','Show all available modules'])
    helplist.extend(['envmaster','list','','Show loaded modules'])
    helplist.extend(['envmaster','help','','Display this message'])
    helplist.extend(['envmaster','disp','mod1 <mod2...>','Display the contents of module(s)'])
    helplist.extend(['envmaster','load','mod1 <mod2...>','Load the specified module(s)'])
    helplist.extend(['envmaster','unload','mod1 <mod2...>','Unload the specified module(s)'])
    helplist.extend(['envmaster','swap','mod1 mod2','Unload mod1 and replace with mod2'])
    helplist.extend(['envmaster','reload','mod1 <mod2...>','Reload with the default version'])
    helplist.extend(['envmaster','allreload','','Reload all loaded modules'])
    helplist.extend(['envmaster','allunload','','Unload all loaded modules'])
    fmt.displayTable(helplist,4)
    
    sys.exit(1)
    

if len(sys.argv) < 3:
    printUsage()
    
shell = sys.argv[1]
action = sys.argv[2]

# create our EnvMasterFile instance
# that does all the work.
modfile = envmasterfile.EnvMasterFile()

if action.startswith('avail'):
    modfile.availModules()
elif action.startswith('list'):
    modfile.listModules()
elif action.startswith('help'):
    printUsage()
elif action.startswith('allreload'):
    modfile.reloadAllModules(shell)
elif action.startswith('allunload'):
    modfile.unloadAllModules(shell)
else:
    # other actions need list of modules
    modlist = sys.argv[3:]
    if len(modlist) == 0:
        printUsage()
    
        
    if action.startswith('disp'):
        modfile.dispModule(modlist)

    elif action.startswith('load'):
        modfile.runModule(shell,modlist,True)

    elif action.startswith('unload'):
        modfile.runModule(shell,modlist,False)
        
    elif action.startswith('sw'):
        if len(modlist) != 2:
            printUsage()
        modfile.runModule(shell,[modlist[0]],False)
        modfile.runModule(shell,[modlist[1]],True)

    elif action.startswith('reload'):
        if len(modlist) == 0:
            printUsage()
        for mod in modlist:
            modfile.runModule(shell, [mod], False)
            modfile.runModule(shell, [mod], True)

    else:
        printUsage()
