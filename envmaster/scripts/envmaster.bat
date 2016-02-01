@echo off
REM This file is part of EnvMaster
REM Copyright (C) 2012  Sam Gillingham
REM
REM This program is free software; you can redistribute it and/or
REM modify it under the terms of the GNU General Public License
REM as published by the Free Software Foundation; either version 2
REM of the License, or (at your option) any later version.
REM
REM This program is distributed in the hope that it will be useful,
REM but WITHOUT ANY WARRANTY; without even the implied warranty of
REM MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
REM GNU General Public License for more details.
REM
REM You should have received a copy of the GNU General Public License
REM along with this program; if not, write to the Free Software
REM Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

REM DOS invocation script for envmaster
REM First we need a temp file to use
REM seems we can't get the pid so make it unique
set TMPFILE=%TMP%\mytempfile-%RANDOM%-%TIME:~6,5%.bat
set envmastercmd=%~dp0\envmastercmd.py

python %envmastercmd% dos %* > %TMPFILE%
call %TMPFILE%
del %TMPFILE%
