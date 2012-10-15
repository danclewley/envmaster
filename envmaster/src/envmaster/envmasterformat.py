"""
Module that handles the 'formated' output from EnvMaster.
In an effort to maintain the look and feel of the orginal
this module takes information about the size of the terminal
and fills it up with text turned into columns or tables.
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
import math
import fcntl
import termios
import struct
from envmasterconf import STDERR

class EnvMasterFormat(object):
    """
    Class that knows the size of the terminal and has 
    methods that display text on it
    """
    def __init__(self):
        # get the size of the terminal
        # obviously only works on Unix, but then so does
        # the whole modules thing...
        data = fcntl.ioctl(STDERR, termios.TIOCGWINSZ,'1234')
        (self.textrows,self.textcols) = struct.unpack('hh', data)
        
    def displayTitle(self,title):
        """
        Given a title pads it out with =
        to go across the terminal
        """
        # put some spaces around it
        paddedtitle = ' %s ' % title 
        # how many equal signs
        nequals = self.textcols - len(paddedtitle)
        # put equals signs on both sizes of the title
        paddedtitle = '=' * int(nequals / 2) + paddedtitle
        paddedtitle += '=' * (self.textcols - len(paddedtitle))
        # write it out
        STDERR.write(paddedtitle + '\n\n')
        
        
    def listAsColumns(self,listdata):
        """
        Given a list of strings, turn it into as many
        columns as will fit in the terminal
        """
        if len(listdata) == 0:
	        return
    
        # find the longest module name + 1(for the space)
        lengthlist = list(map(len,listdata))
        maxlength = max(lengthlist) + 1
        
        # how many columns does that mean?
        ncolumns = int(min(self.textcols / maxlength,len(listdata)))
        
        # how many rows
        nrows = int(math.ceil(len(listdata) / float(ncolumns)))
        
        # how much buffering on the left to centre everything
        nleftbuffer = int((self.textcols - (maxlength * ncolumns)) / 2)
        
        for row in range(nrows):
            # start with the buffering on the left
            bufferstr = ' ' * nleftbuffer
            for col in range(ncolumns):
                # make sure we keep the order of the list
                # going down the columns
                index = col*nrows+row
                if index < len(listdata): # careful if len(listdata) < number of rows*cols
                    name = listdata[index]
                    bufferstr += name
                    # buffer it out to maxlength
                    bufferstr += ' ' * (maxlength - len(name))
            STDERR.write(bufferstr + '\n')
        STDERR.write('\n')
            
    @staticmethod
    def trimString(string, amounttotrim):
        """
        Used if there is too much info to fit in the
        terminal. Creates a string that is shorty
        by amounttotrim and inserts '...' in the middle
        """
        if amounttotrim == 0:
            return string

        elif len(string) - amounttotrim > 5:
    
            halfamounttoleave = (len(string) - amounttotrim - 3) / 2
        
            firstpart = string[:halfamounttoleave]
            secondpart = string[-halfamounttoleave:]
    
            return firstpart + '...' + secondpart
        else:
            # best we can do
            return string[0] + '...' + string[-1]

    def displayTable(self,listdata,ncols):
        """
        In the case of module disp, we have a list of data
        that actually needs to be displayed in a table as we 
        have added to it ncols items at a time and these
        items must be displayed across, not down like
        listAsColumns().
        """
        # work out the max size of the text
        # in each comlum
        colsizes = []
        for col in range(ncols):
            collist = [] # get the items for this column
            index = col
            while index < len(listdata):
                collist.append(listdata[index])
                index += ncols
            # get the max size of the text in this col
            collistlength = list(map(len,collist))
            colsizes.append(max(collistlength) + 1)
            
        # number of spaces on the left to centre it
        nleftbuffer = int((self.textcols - sum(colsizes)) / 2)
        
        if nleftbuffer < 0:
            # it's not all going to fit
            # find the biggest colsize and trim it down
            coltotrim = colsizes.index(max(colsizes))
            amounttotrim = sum(colsizes) - self.textcols 
            colsizes[coltotrim] = colsizes[coltotrim] - amounttotrim
            nleftbuffer = 0
        else:
            # nothing needs trimming
            coltotrim = -1
            
        nrows = int(len(listdata) / ncols)
        index = 0
        for row in range(nrows):
            # space on the left to centre
            bufferstr = ' ' * nleftbuffer
            for col in range(ncols):
                data = listdata[index]
                
                if col == coltotrim and len(data) > colsizes[col]:
                    # we need to trim this one
                    data = self.trimString(data, len(data) - colsizes[col])
                    
                bufferstr += data
                    
                # pad out so all the same size
                bufferstr += ' ' * (colsizes[col] - len(data))
                    
                index += 1
            STDERR.write(bufferstr + '\n')
        STDERR.write('\n')
