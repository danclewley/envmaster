#!/usr/bin/env python
"""
The setup script for EnvMaster. Creates the module, installs
the scripts and the init files. 
Good idea to use 'install --prefix=/opt/xxxxx' so not installed
with Python.
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
from distutils.core import setup
import sys
import glob
import envmaster

scriptList = ['scripts/envmastercmd.py','scripts/mod2envmaster.py']
if sys.platform == 'win32':
    scriptList.append('scripts/envmaster.bat')

setup(name='EnvMaster',
      version=envmaster.ENVMASTER_VERSION,
      description='Python implementation of Unix modules',
      author='Sam Gillingham',
      author_email='gillingham.sam@gmail.com',
      packages=['envmaster'],
      package_dir={'envmaster' : 'envmaster'},
      scripts=scriptList,
      data_files=[('init',glob.glob('init/*'))],
     )
