
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
import jt_wire_text


def load_ui():
    current_script_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    if (cmds.window('jt_y_slider', exists=True)):
        cmds.deleteUI('jt_y_slider')

    window = cmds.loadUI(uiFile=os.path.join(current_script_path, 'jt_y_slider.ui'))

    # set node list select change command
    cmds.textScrollList('jt_y_slider_node_list', e=True, sc='import jt_y_slider;jt_y_slider.ui_refresh_attributes()', allowMultiSelection=False)
    
    cmds.textScrollList('jt_y_slider_attr_list', e=True, allowMultiSelection=True)

    ui_refresh_attributes()

    cmds.showWindow(window)



def ui_refresh_nodes():
    selection = cmds.ls(sl=True)

    if selection:
        attrs = cmds.listAttr(selection[0], keyable=True)

        cmds.textScrollList('jt_y_slider_node_list', e=True, ra=True)
        cmds.textScrollList('jt_y_slider_node_list', e=True, append='<none>')
        cmds.textScrollList('jt_y_slider_node_list', e=True, append=selection[0])
        for node in cmds.listRelatives(selection[0]):
            cmds.textScrollList('jt_y_slider_node_list', e=True, append=node)
            for connection in cmds.listConnections(node):
                if cmds.nodeType(connection) == 'blendShape':
                    cmds.textScrollList('jt_y_slider_node_list', e=True, append=connection)

    
def ui_refresh_attributes():
    cmds.textScrollList('jt_y_slider_attr_list', e=True, ra=True)
    nodes = cmds.textScrollList('jt_y_slider_node_list', q=True, si=True)

    if nodes:
        node = nodes[0]
        if not str(node) == '<none>':
            node_type = cmds.nodeType(node)
            # list all blend_shape attrs
            if node_type == 'blendShape':
                for attr in cmds.listAttr(node + '.weight', keyable=True, m=True):
                    cmds.textScrollList('jt_y_slider_attr_list', e=True, append=attr)
            else:
                attrs = cmds.listAttr(node, keyable=True, visible=True)
                if attrs is not None:
                    for attr in attrs:
                        cmds.textScrollList('jt_y_slider_attr_list', e=True, append=attr)


def ui_create():
    nodes = cmds.textScrollList('jt_y_slider_node_list', q=True, si=True)
    attrs = cmds.textScrollList('jt_y_slider_attr_list', q=True, si=True)

    attribute_names = []

    if nodes:

        if attrs is not None:
            for attr in attrs:
                attribute_names.append(nodes[0] + '.' + attr)

    name = cmds.textField('jt_y_slide_name_field', q=True, tx=True)

    high        = float(cmds.textField('jt_y_slide_high_field', q=True, tx=True))
    low         = float(cmds.textField('jt_y_slide_low_field', q=True, tx=True))
    init_value  = float(cmds.textField('jt_y_slide_init_value_field', q=True, tx=True))


    if attribute_names is not []:
        move_incriment = 0
        for i in range(len(attribute_names)):
            slider_group = create_y_slider(attrs[i], low, high, init_value, attribute_names[i]) 
            cmds.move(move_incriment, 0,0, slider_group, r=True)
            move_incriment += 3

    else:
        create_y_slider(name, low, high, init_value) 


def create_y_slider(name, low=0, high=1, init=0, attribute=False):
    
    if high < low:
        high_temp = high
        low_temp = low
        
        high = low_temp
        low = high_temp
    
    high = float(high)
    low = float(low)
    
    length = high - low
    
    rail_points  = [(0, 0 , 0),
                    (0, 1, 0)]
                   
    frame_points = [(-0.15, -0.07, 0), 
                    ( 0.15, -0.07, 0), 
                    ( 0.15,  1.07, 0), 
                    (-0.15,  1.07, 0), 
                    (-0.15, -0.07, 0)]
                    
    slider_points = [(-0.13,  -0.05, 0),
                     ( 0.13,  -0.05, 0),
                     ( 0.13,   0.05, 0),
                     (-0.13,   0.05, 0),
                     (-0.13,  -0.05, 0)]

    text = jt_wire_text.create(name)
    cmds.setAttr(text + '.scaleX', 0.26)
    cmds.setAttr(text + '.scaleY', 0.26)
    cmds.setAttr(text + '.scaleZ', 0.26)
    text_length = cmds.xform(text, q=True, bb=True)[3]
    if text_length > 1.0:
        cmds.scale( 1/text_length, 1, 1, r=True)
    cmds.setAttr(text + '.translateX', 0.13)
    cmds.setAttr(text + '.rotateZ', 90)

    frame = cmds.curve(d=1, p=frame_points,  n=name + '_frame')
    slider = cmds.curve(d=1, p=slider_points, n=name + '_slider')

    cmds.setAttr(slider + '.overrideEnabled', 1)
    cmds.setAttr(slider + '.overrideColor', 13)


    for item in (frame, text):
        cmds.setAttr(item + '.overrideEnabled', 1)
        cmds.setAttr(item + '.overrideDisplayType', 1)

    cmds.select(slider, r=True)
    slider_group = cmds.group(n=name + '_slider_group')

    # normalise and position everything
    
    normalise_coeff = 1.0 / length
    
    cmds.setAttr(slider + '.translateY', init)
    cmds.setAttr(slider_group + '.scaleY', normalise_coeff)
    cmds.setAttr(slider_group + '.translateY', - (low * normalise_coeff))
    cmds.setAttr(slider + '.scaleY', 1.0 / normalise_coeff)

    cmds.select(text, frame, slider_group, r=True)
    cmds.parent()
    
    cmds.move(-0.15, 1.07, 0, slider_group + '.scalePivot', slider_group + '.rotatePivot', ws=True, a=True)
    
    # lock and hide attributes
    for attr in ('tx', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'):
        cmds.setAttr(slider + '.' + attr, keyable=False, channelBox=False, lock=True)
        
    cmds.select(slider_group, r=True)
    cmds.scale(10,10,10, r=True)

    if attribute:
        cmds.connectAttr(slider + '.translateY', attribute, f=True)

    return slider_group
    
