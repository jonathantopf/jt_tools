
#
# Copyright (c) 2013 Jonathan Topf
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#


import maya.cmds as cmds

def create():

    selection_positions = cmds.xform(q=True, ws=True, t=True)

    high_pos = selection_positions[0:3]
    low_pos  = selection_positions[0:3]

    for i in range(len(selection_positions) / 3):
        start_index = i * 3
        list_section = selection_positions[start_index:start_index + 3] 
        
        for i in (range(3)):
            if list_section[i] > high_pos[i]: high_pos[i] = list_section[i]
            if list_section[i] < low_pos[i]: low_pos[i] = list_section[i]
            

    average_pos = [0,0,0]
    for i in (range(3)):
        average_pos[i] = (high_pos[i] + low_pos[i]) / 2

    locator = cmds.spaceLocator()
    cmds.xform(locator, t=average_pos, ws=True)