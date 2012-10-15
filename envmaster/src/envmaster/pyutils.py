"""
Module to use for loading/unloading modules
directly from Python. This method uses the
'pythonsilent' shell to ensure nothing is
written to stdout, but the environment is
updated anyway due to the way EnvMaster updates
the environment of the current process.
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

import envmasterfile

def load(*modnames):
    """
    Load the specified module names
    """
    modfile = envmasterfile.EnvMasterFile()
    modfile.runModule('pythonsilent',modnames,True)


def unload(*modnames):
    """
    Unload the specified module names
    """
    modfile = envmasterfile.EnvMasterFile()
    modfile.runModule('pythonsilent',modnames,False)
