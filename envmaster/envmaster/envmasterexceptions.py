"""
All the EnvMaster exceptions live in this module
to make them accessible from all the modules.
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

class EnvMasterException(SystemExit):
    """
    Base class of all the EnvMaster exceptions
    """
    pass
    
class EnvMasterPathException(EnvMasterException):
    """
    There was a problem with the path passed in.
    """
    pass
    
class EnvMasterParseError(EnvMasterException):
    """
    Unable to parse specified module
    """
    pass
    
class EnvMasterNoModule(EnvMasterException):
    """
    Unable to find specified module
    """
    pass

class EnvMasterPrereqFailed(EnvMasterException):
    """
    A prereq statement failed because the specififed
    module(s) are not loaded
    """
    pass

class EnvMasterConflictFailed(EnvMasterException):
    """
    A conflict statement failed because the specififed
    module(s) are loaded
    """
    pass
    
class EnvMasterNoModules(EnvMasterException):
    """
    No module files were found
    """
    pass
