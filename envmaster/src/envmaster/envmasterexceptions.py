"""
All the EnvMaster exceptions live in this module
to make them accessible from all the modules.
"""

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
