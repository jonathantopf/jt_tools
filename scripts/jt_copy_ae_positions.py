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
import os
import inspect

def load_ui():

    current_script_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    if (cmds.window('jt_copy_ae_positions', exists=True)):
        cmds.deleteUI('jt_copy_ae_positions')
    window = cmds.loadUI(uiFile=os.path.join(current_script_path, 'jt_copy_ae_positions.ui'))
    cmds.showWindow(window)


def ui_set_positions():

    selection = cmds.ls(sl=True, tr=True)
    if selection > 0:
        transform = selection[0]
    else:
        cmds.warning('No valid selection')
        return

    ae_text = cmds.scrollField('jt_copy_ae_positions_text_box', q=True, tx=True)
    start_is_origin = cmds.checkBox('jt_copy_ae_positions_start_is_origin_check', q=True, value=True)
    maintain_offset = cmds.checkBox('jt_copy_ae_positions_maintain_offset', q=True, value=True)
    unit_scale = cmds.textField('jt_copy_ae_positions_unit_scale', q=True, tx=True)
    set_positions_from_text(transform, ae_text, start_is_origin, float(unit_scale), maintain_offset)


def set_positions_from_text(transform, position_text, start_is_origin, unit_scale, maintain_offset):

    start_marker = 'Position'
    position_data = position_text.split(start_marker)[1] # split off ehader data
    position_data = position_data.split('\n') # transform to list of lines
    position_data = position_data[2:-4] # split off start and end trailing lines

    start_position = cmds.getAttr(transform + '.translate')[0]

    for i in range(len(position_data)):
        position_data[i] = position_data[i].split('\t')[1:-1]
        
        for n in range(4):
            position_data[i][n] = float(position_data[i][n])

    # apply unit scale
    for i in range(len(position_data)):
        for n in (1,2,3):
            position_data[i][n] = position_data[i][n] * unit_scale

    # negate start position
    if start_is_origin:
        origin = position_data[0][:]  
        for i in range(len(position_data)):
            for n in (1,2,3):
                position_data[i][n] = position_data[i][n] - origin[n]

    # add offset
    if maintain_offset:
        for i in range(len(position_data)):
            for n in (1,2,3):
                position_data[i][n] = position_data[i][n] + start_position[n-1]

    set_positions(transform, position_data)


def set_positions(transform, positions):
    
    start_time = cmds.currentTime(q=True)

    for row in positions:
        cmds.currentTime(row[0], u=False)
        cmds.setAttr(transform + '.translate', row[1], row[2], row[3])
        cmds.setKeyframe(transform + '.translate')

    cmds.currentTime(start_time)










