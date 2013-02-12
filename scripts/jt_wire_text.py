
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

# To create a new control curve use the code below to print out the points of a selected curve as an array of tuples
# curve_name = cmds.ls(sl=True)[0]
# curve_points = cmds.getAttr(curve_name + '.cv[*]')
# print curve_points

def load_ui():
    current_script_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    if (cmds.window('jt_wire_text', exists=True)):
        cmds.deleteUI('jt_wire_text')

    window = cmds.loadUI(uiFile=os.path.join(current_script_path, 'jt_wire_text.ui'))
    cmds.showWindow(window)


letters = {
    
    'a': (0.5 , [(0.0, 1.0, 0.0), (0.5, 1.0, 0.0), (0.5, 0.5, 0.0), (0.0, 0.5, 0.0), (0.0, 0.0, 0.0), (0.5, 0.0, 0.0), (0.5, 0.5, 0.0)]),
    'b': (0.5 , [(0.0, 2.0, 0.0), (0.0, 0.0, 0.0), (0.5, 0.0, 0.0), (0.5, 1.0, 0.0), (0.0, 1.0, 0.0)]),
    'c': (0.5 , [(0.5, 1.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 0.0), (0.5, 0.0, 0.0)]),
    'd': (0.5 , [(0.5, 1.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 0.0), (0.5, 0.0, 0.0), (0.5, 2.0, 0.0)]),
    'e': (0.5 , [(0.0, 0.5, 0.0), (0.5, 0.5, 0.0), (0.5, 1.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 0.0), (0.5, 0.0, 0.0)]),
    'f': (0.5 , [(0.5, 1.0, 0.0), (0.0, 1.0, 0.0), (0.0, -1.0, 0.0), (0.0, 0.0, 0.0), (0.5, 0.0, 0.0)]),
    'g': (0.5 , [(0.5, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.5, 1.0, 0.0), (0.5, -1.0, 0.0), (0.0, -1.0, 0.0)]),
    'h': (0.5 , [(0.0, 2.0, 0.0), (0.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.5, 1.0, 0.0), (0.5, 0.0, 0.0)]),
    'i': (0   , [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0)]),
    'j': (0.5 , [(0.025, -0.5, 0.0), (0.5, 0.0, 0.0), (0.5, 1.0, 0.0)]),
    'k': (0.5 , [(0.0, 0.0, 0.0), (0.0, 2.0, 0.0), (0.0, 1.0, 0.0), (0.5, 1.0, 0.0), (0.5, 0.5, 0.0), (0.0, 0.5, 0.0), (0.5, 0.0, 0.0)]),
    'l': (0   , [(0.0, 2.0, 0.0), (0.0, 0.0, 0.0)]),
    'm': (0.5 , [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.25, 0.0, 0.0), (0.5, 1.0, 0.0), (0.5, 0.0, 0.0)]),
    'n': (0.5 , [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.5, 0.0, 0.0), (0.5, 1.0, 0.0)]),
    'o': (0.5 , [(0.0, 1.0, 0.0), (0.0, 0.0, 0.0), (0.5, 0.0, 0.0), (0.5, 1.0, 0.0), (0.0, 1.0, 0.0)]),
    'p': (0.5 , [(0.0, -1.0, 0.0), (0.0, 1.0, 0.0), (0.5, 1.0, 0.0), (0.5, 0.0, 0.0), (0.0, 0.0, 0.0)]),
    'q': (0.5 , [(0.5, -1.0, 0.0), (0.5, 1.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 0.0), (0.5, 0.0, 0.0)]),
    'r': (0.5 , [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.5, 1.0, 0.0)]),
    's': (0.5 , [(0.5, 1.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.5, 0.0), (0.5, 0.5, 0.0), (0.5, 0.0, 0.0), (0.0, 0.0, 0.0)]),
    't': (0.5 , [(0.0, 2.0, 0.0), (0.0, 0.0, 0.0), (0.5, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.5, 1.0, 0.0)]),
    'u': (0.5 , [(0.0, 1.0, 0.0), (0.0, 0.0, 0.0), (0.5, 0.0, 0.0), (0.5, 1.0, 0.0)]),
    'v': (0.5 , [(0.0, 1.0, 0.0), (0.25, 0.0, 0.0), (0.5, 1.0, 0.0)]),
    'w': (1   , [(0.0, 1.0, 0.0), (0.25, 0.0, 0.0), (0.5, 1.0, 0.0), (0.75, 0.0, 0.0), (1.0, 1.0, 0.0)]),
    'x': (0.5 , [(0.0, 0.0, 0.0), (0.5, 1.0, 0.0), (0.25, 0.5, 0.0), (0.0, 1.0, 0.0), (0.5, 0.0, 0.0)]),
    'y': (0.5 , [(0.0, 1.0, 0.0), (0.0, 0.0, 0.0), (0.5, 0.0, 0.0), (0.5, 1.0, 0.0), (0.5, -1.0, 0.0), (0.0, -1.0, 0.0)]),
    'z': (0.5 , [(0.0, 1.0, 0.0), (0.5, 1.0, 0.0), (0.0, 0.0, 0.0), (0.5, 0.0, 0.0)]),
    '1': (0   , [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0)]),
    '2': (0.5 , [(0.0, 1.0, 0.0), (0.5, 1.0, 0.0), (0.5, 0.5, 0.0), (0.0, 0.0, 0.0), (0.5, 0.0, 0.0)]),
    '3': (0.5 , [(0.0, 1.0, 0.0), (0.5, 1.0, 0.0), (0.0, 0.5, 0.0), (0.5, 0.5, 0.0), (0.5, 0.0, 0.0), (0.0, 0.0, 0.0)]),
    '4': (0.5 , [(0.0, 1.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.5, 0.0), (0.5, 0.5, 0.0), (0.5, 1.0, 0.0)]),
    '5': (0.5 , [(0.5, 1.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.5, 0.0), (0.5, 0.5, 0.0), (0.5, 0.0, 0.0), (0.0, 0.0, 0.0)]),
    '6': (0.5 , [(0.5, 1.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 0.0), (0.5, 0.0, 0.0), (0.5, 0.5, 0.0), (0.0, 0.5, 0.0)]),
    '7': (0.5 , [(0.0, 1.0, 0.0), (0.5, 1.0, 0.0), (0.0, 0.0, 0.0)]),
    '8': (0.5 , [(0.5, 1.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 0.0), (0.5, 0.0, 0.0), (0.5, 1.0, 0.0), (0.5, 0.5, 0.0), (0.0, 0.5, 0.0)]),
    '9': (0.5 , [(0.5, 0.5, 0.0), (0.0, 0.5, 0.0), (0.0, 1.0, 0.0), (0.5, 1.0, 0.0), (0.5, 0.0, 0.0), (0.0, 0.0, 0.0)]),
    '0': (0.5 , [(0.5, 1.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 0.0), (0.5, 0.0, 0.0), (0.5, 1.0, 0.0), (0.0, 0.0, 0.0)]),
    ',': (0.5 , [(0.0, 0.0, 0.0), (0.0, -0.2516783676397859, 0.0)]),
    '-': (0.5 , [(0.0, 0.5, 0.0), (0.5, 0.5, 0.0)]),
    '.': (0.5 , [(-0.099999999999997868, 0.10000000000000001, 0.0), (0.10000000000000142, -0.10000000000000001, 0.0), (0.0, 0.0, 0.0), (0.10000000000000142, 0.10000000000000001, 0.0), (-0.099999999999997868, -0.10000000000000001, 0.0)]),
    '(': (0.5 , [(0.32226251916916837, 0.0, 0.0), (0.0, 0.5, 0.0), (0.32226251916916837, 1.0, 0.0)]),
    ')': (0.5 , [(0.0, 0.0, 1.2246467991473532e-16), (0.32226251916916837, 0.5, 1.2246467991473532e-16), (0.0, 1.0, 1.2246467991473532e-16)]),
    '_': (0.5 , [(0.0, 0.0, 0.0), (0.5, 0.0, 0.0)])

}


def ui_create():

    text = cmds.textField('jt_wire_text_input', q=True, tx=True)
    create(text)


def create(text):

    text = str(text).lower()
    char_list = list(text)

    curser_pos = 0.0
    letter_curve_list = []

    for char in char_list:
        char_keys = letters.keys()
        if char in char_keys:
            curve = cmds.curve(degree=1, p=letters[char][1])
            cmds.setAttr(curve + '.translateX', curser_pos)
            curser_pos += letters[char][0] + 0.2
            letter_curve_list.append(curve)
        elif char == ' ':
            curser_pos += 0.7

    cmds.select(letter_curve_list, r=True)
    cmds.group()
    cmds.xform(os=True, piv=(0,0,0))






