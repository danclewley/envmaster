"""
Module to use for loading/unloading modules
directly from Python. This method uses the
'pythonsilent' shell to ensure nothing is
written to stdout, but the environment is
updated anyway due to the way EnvMaster updates
the environment of the current process.
"""

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
