#!/usr/bin/env python
"""
The setup script for EnvMaster. Creates the module, installs
the scripts and the init files. 
Good idea to use 'install --prefix=/opt/xxxxx' so not installed
with Python.
"""
from distutils.core import setup
import glob

setup(name='EnvMaster',
      version='0.1.2',
      description='Python implementation of Unix modules',
      author='Sam Gillingham',
      author_email='gillingham.sam@gmail.com',
      packages=['envmaster'],
      package_dir={'envmaster' : 'src/envmaster'},
      scripts=['scripts/envmastercmd.py','scripts/mod2envmaster.py'],
      data_files=[('init',glob.glob('init/*'))],
     )
