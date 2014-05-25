
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
import jt_ctl_curve
import jt_compile_to_nodes as comp
import os
import inspect
import ast

reload(jt_ctl_curve)

#--------------------------------------------------------------------------------------------------
# helper functions.
#--------------------------------------------------------------------------------------------------

def load_ui():

    current_script_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    if (cmds.window('jt_autorig', exists=True)):
        cmds.deleteUI('jt_autorig')
    window = cmds.loadUI(uiFile=os.path.join(current_script_path, 'jt_autorig.ui'))
    cmds.showWindow(window)


def duplicate_joint_without_children(joint, postfix):

    new_joint_name = joint + postfix
    cmds.select(joint, r=True)
    cmds.duplicate(n=new_joint_name)
    if cmds.listRelatives(ap=True) is not None:
        cmds.parent(w=True)
    if cmds.listRelatives(new_joint_name, ad=True, fullPath=True):
        cmds.delete(cmds.listRelatives(new_joint_name, ad=True, fullPath=True))
    return new_joint_name


def add_keyable_attr(obj, attr, type='float'):

    cmds.select(obj)
    if type == 'float':
        cmds.addAttr(ln=attr, at='double')
    elif type == 'bool':
        cmds.addAttr(ln=attr, at='bool')
    cmds.setAttr(obj + '.' + attr, cb=True)
    cmds.setAttr(obj + '.' + attr, keyable=True)

def add_label_attr(obj, attr):

    cmds.select(obj)
    cmds.addAttr(ln=attr, at='bool')
    cmds.setAttr(obj + '.' + attr, cb=True)
    cmds.setAttr(obj + '.' + attr, keyable=False)


def change_prefix(string, new_prefix):

    string_list = list(string)
    string_list[0] = new_prefix[0]
    return ''.join(string_list)


def create_blend(attr_1, attr_2, out, controll_attribute):

    blend_node = cmds.createNode('blendColors', n=out.replace('.', '_') + '_blend')
    cmds.connectAttr(attr_1, blend_node + '.color2', f=True)
    cmds.connectAttr(attr_2, blend_node + '.color1', f=True)
    cmds.connectAttr(controll_attribute, blend_node + '.blender', f=True)
    cmds.connectAttr(blend_node + '.output', out, f=True)
    return blend_node


def add_node_to_rig_nodes(base_curve, section, node_names):

    current_nodes_data = cmds.getAttr(base_curve + '.rig_nodes')
    node_dict = ast.literal_eval(current_nodes_data)

    # turn node names into list is it is not already
    if (type(node_names) is str) or (type(node_names) is unicode):
        node_names = [node_names]

    for node_name in node_names:
        # add the section if its not already tehre
        if not section in node_dict:
            node_dict[section] = []
        node_dict[section].append(node_name)

    cmds.setAttr(base_curve + '.rig_nodes', str(node_dict), type='string')

    return node_name


def list_rig_nodes(base_curve):

    current_nodes_data = cmds.getAttr(base_curve + '.rig_nodes')
    return ast.literal_eval(current_nodes_data)


def de_rig_element(base_curve, rig_element, root_bone=None):

    rig_nodes = list_rig_nodes(base_curve)
    for key in rig_nodes.keys():
        if key == rig_element:
            for item in rig_nodes[rig_element]:
                if cmds.objExists(item):
                    cmds.select(item, r=True)
                    cmds.delete()
            # update dict
            del rig_nodes[key]
            cmds.setAttr(base_curve + '.rig_nodes', str(rig_nodes), type='string')

    # if a root bone is set select the heirarchy an set all rotations to 0
    if root_bone is not None:
        cmds.select(root_bone, hi=True, r=True)
        for object in cmds.ls(sl=True):
            cmds.setAttr(object + '.rotate', 0,0,0)

    else:
        cmds.warning('{0} does not exist, cannot de-rig'.format(rig_element))


def create_clamp(attr, name, low, high):

    node = cmds.createNode('clamp', n=name)
    cmds.connectAttr(attr, node + '.inputR', f=True)

    if (type(low) is str) or (type(low) is unicode):
        cmds.connectAttr(low, node + '.minR', f=True)
    else:
        cmds.setAttr(node + '.minR', low)

    if (type(high) is str) or (type(high) is unicode):
        cmds.connectAttr(high, node + '.maxR', f=True)
    else:
        cmds.setAttr(node + '.maxR', high)

    return node


def create_mult(attr, name, mult_coeff):
    
    node = cmds.createNode('multiplyDivide', n=name)
    cmds.connectAttr(attr, node + '.input1X', f=True)

    if (type(mult_coeff) is str) or (type(mult_coeff) is unicode):
        cmds.connectAttr(mult_coeff, node + '.input2X', f=True)
    else:
        cmds.setAttr(node + '.input2X', mult_coeff)

    return node


def create_add(attr, name, add_value):
    
    node = cmds.createNode('plusMinusAverage', n=name)
    cmds.connectAttr(attr, node + '.input1D[0]', f=True)

    if (type(add_value) is str) or (type(add_value) is unicode):
        cmds.connectAttr(add_value, node + '.input1D[1]', f=True)
    else:
        cmds.setAttr(node + '.input1D[1]', add_value)

    return node


def create_joint_proxy(joint_name='locator'):

    root_curve = jt_ctl_curve.create_shape(joint_name, 'sphere')

    cmds.setAttr(root_curve + '.overrideEnabled', 1)
    cmds.setAttr(root_curve + '.overrideColor', 16)

    x_arrow = jt_ctl_curve.create_shape(joint_name + '_x_arrow', 'arrow')
    y_arrow = jt_ctl_curve.create_shape(joint_name + '_y_arrow', 'arrow')
    z_arrow = jt_ctl_curve.create_shape(joint_name + '_z_arrow', 'arrow')

    cmds.setAttr(x_arrow + '.overrideColor', 13)
    cmds.rotate(0,0,-90, x_arrow, r=True, os=True)

    cmds.setAttr(y_arrow + '.overrideColor', 14)

    cmds.setAttr(z_arrow + '.overrideColor', 6)
    cmds.rotate(90,0,0, z_arrow, r=True, os=True)

    for item in (x_arrow, y_arrow, z_arrow):
        cmds.setAttr(item + '.overrideEnabled', 1)

        for attr in ('rotate', 'translate', 'scale'):
            cmds.setAttr(item + '.' + attr, lock=True, keyable=False, channelBox=False)

    cmds.parent(x_arrow, y_arrow, z_arrow, root_curve)

    cmds.select(root_curve)

    return root_curve


#--------------------------------------------------------------------------------------------------
# ui functions.
#--------------------------------------------------------------------------------------------------

def ui_create_proxy_skeleton():
    create_proxy_skeleton()


def ui_create_skeleton_from_proxy():
    
    dial_response = cmds.confirmDialog(message='would you like to save a copy of this scene before creating a skeleton', button=['cancel', 'no', 'yes'])
    if dial_response == 'cancel':
        return
    elif dial_response == 'yes':

        initial_file_path = cmds.file(q=True, sn=True)
        bone_file_path = initial_file_path.replace('.ma', '').replace('.mb', '') + '_bones.ma'

        cmds.file(rename=bone_file_path)
        cmds.file(force=True, save=True, type='mayaAscii')

        cmds.file(rename=initial_file_path)
        cmds.file(force=True, save=True, type='mayaAscii')

    create_skeleton_from_proxy()


def ui_create_base_rig():

    cog = cmds.textField('jt_autorig_base_cog_select_text', q=True, tx=True)
    rig_region_name = 'cog'
    create_base_rig(cog, rig_region_name)


def ui_remove_base_rig():

    base_curve = cmds.textField('jt_autorig_base_name_select_text', q=True, tx=True)
    if cmds.objExists(base_curve):
        cmds.select(base_curve, r=True)
        cmds.delete()
    else:
        cmds.warning('{0} does not exist, cannot de-rig'.format(base_curve))

def ui_create_arm_rig():

    base_curve = cmds.textField('jt_autorig_base_name_select_text', q=True, tx=True)
    clavicle = cmds.textField('jt_autorig_arms_clavicle_select_text', q=True, tx=True)
    shoulder = cmds.textField('jt_autorig_arms_shoulder_select_text', q=True, tx=True)
    elbow    = cmds.textField('jt_autorig_arms_elbow_select_text', q=True, tx=True)
    forearm  = cmds.textField('jt_autorig_arms_forearm_select_text', q=True, tx=True)
    wrist    = cmds.textField('jt_autorig_arms_wrist_select_text', q=True, tx=True)
    hand     = cmds.textField('jt_autorig_arms_hand_select_text', q=True, tx=True)
    rig_l    = cmds.checkBox('jt_autorig_arms_rig_L', q=True, value=True)
    rig_r    = cmds.checkBox('jt_autorig_arms_rig_R', q=True, value=True)

    if rig_l:
        rig_region_name = 'L_arm'
        create_arm_rig(base_curve, rig_region_name, clavicle, shoulder, elbow, forearm, wrist, hand, 'L')
    if rig_r:
        rig_region_name = 'R_arm'
        create_arm_rig(base_curve, rig_region_name, clavicle, shoulder, elbow, forearm, wrist, hand, 'R')


def ui_remove_arm_rig():

    base_curve = cmds.textField('jt_autorig_base_name_select_text', q=True, tx=True)
    clavicle = cmds.textField('jt_autorig_arms_clavicle_select_text', q=True, tx=True)
    rig_l    = cmds.checkBox('jt_autorig_arms_rig_L', q=True, value=True)
    rig_r    = cmds.checkBox('jt_autorig_arms_rig_R', q=True, value=True)

    if rig_l:
        de_rig_element(base_curve, 'L_arm', change_prefix(clavicle, 'L'))
    if rig_r:
        de_rig_element(base_curve, 'R_arm', change_prefix(clavicle, 'R'))


def ui_create_hand_rig():

    base_curve  = cmds.textField('jt_autorig_base_name_select_text', q=True, tx=True)
    hand        = cmds.textField('jt_autorig_hand_hand_select_text', q=True, tx=True)
    ring_cup    = cmds.textField('jt_autorig_hand_ring_cup_select_text', q=True, tx=True)
    pinky_cup   = cmds.textField('jt_autorig_hand_pinky_cup_select_text', q=True, tx=True)
    thumb_base  = cmds.textField('jt_autorig_hand_thumb_base_select_text', q=True, tx=True)
    index_base  = cmds.textField('jt_autorig_hand_index_base_select_text', q=True, tx=True)
    middle_base = cmds.textField('jt_autorig_hand_middle_base_select_text', q=True, tx=True)
    ring_base   = cmds.textField('jt_autorig_hand_ring_base_select_text', q=True, tx=True)
    pinky_base  = cmds.textField('jt_autorig_hand_pinky_base_select_text', q=True, tx=True)
    rig_l       = cmds.checkBox('jt_autorig_hands_rig_L', q=True, value=True)
    rig_r       = cmds.checkBox('jt_autorig_hands_rig_R', q=True, value=True)

    if rig_l:
        rig_region_name = 'L_hand'
        create_hand_rig(base_curve, rig_region_name, hand, ring_cup, pinky_cup, thumb_base, index_base, middle_base, ring_base, pinky_base, 'L')
    if rig_r:
        rig_region_name = 'R_hand'
        create_hand_rig(base_curve, rig_region_name, hand, ring_cup, pinky_cup, thumb_base, index_base, middle_base, ring_base, pinky_base, 'R')


def ui_remove_hand_rig():

    base_curve  = cmds.textField('jt_autorig_base_name_select_text', q=True, tx=True)
    hand        = cmds.textField('jt_autorig_hand_hand_select_text', q=True, tx=True)
    rig_l       = cmds.checkBox('jt_autorig_hands_rig_L', q=True, value=True)
    rig_r       = cmds.checkBox('jt_autorig_hands_rig_R', q=True, value=True)

    if rig_l:
        de_rig_element(base_curve, 'L_hand', hand)
    if rig_r:
        de_rig_element(base_curve, 'R_hand', hand)


def ui_create_leg_rig():

    base_curve            = cmds.textField('jt_autorig_base_name_select_text', q=True, tx=True)
    pelvis                = cmds.textField('jt_autorig_legs_pelvis_select_text', q=True, tx=True)
    hip                   = cmds.textField('jt_autorig_legs_hip_select_text', q=True, tx=True)
    knee                  = cmds.textField('jt_autorig_legs_knee_select_text', q=True, tx=True)
    ankle                 = cmds.textField('jt_autorig_legs_ankle_select_text', q=True, tx=True)
    override_region_name  = cmds.textField('jt_autorig_leg_rig_override_region_text', q=True, tx=True)
    l_prefix              = cmds.checkBox('jt_autorig_leg_rig_L', q=True, value=True)
    r_prefix              = cmds.checkBox('jt_autorig_leg_rig_R', q=True, value=True)
    none_prefix           = cmds.checkBox('jt_autorig_leg_rig_none', q=True, value=True)
    override_region_check = cmds.checkBox('jt_autorig_leg_rig_override_region_check', q=True, value=True)

    rig_region_name = override_region_name

    if l_prefix:
        if not override_region_check:
            rig_region_name = 'L_leg'
        create_leg_rig(base_curve, rig_region_name, pelvis, hip, knee, ankle, 'L')

    if r_prefix:
        if not override_region_check:
            rig_region_name = 'R_leg'
        create_leg_rig(base_curve, rig_region_name, pelvis, hip, knee, ankle, 'R')

    if none_prefix:
        if not override_region_check:
            cmds.warning('set overide region name')
            return
        create_leg_rig(base_curve, rig_region_name, pelvis, hip, knee, ankle, 'R')


def ui_select_leg_rig_joint(text_field):
    
    selection = cmds.ls(sl=True, typ='joint')
    if len(selection) == 0:
        cmds.warning('no joint selected')
        return

    selection_name = selection[0].replace('L', '<prefix>').replace('R', '<prefix>')
    cmds.textField(text_field, e=True, tx=selection_name)


def ui_remove_leg_rig():

    base_curve = cmds.textField('jt_autorig_base_name_select_text', q=True, tx=True)
    hip        = cmds.textField('jt_autorig_legs_hip_select_text', q=True, tx=True)
    override_region_name  = cmds.textField('jt_autorig_leg_rig_override_region_text', q=True, tx=True)
    l_prefix              = cmds.checkBox('jt_autorig_leg_rig_L', q=True, value=True)
    r_prefix              = cmds.checkBox('jt_autorig_leg_rig_R', q=True, value=True)
    none_prefix           = cmds.checkBox('jt_autorig_leg_rig_none', q=True, value=True)
    override_region_check = cmds.checkBox('jt_autorig_leg_rig_override_region_check', q=True, value=True)

    rig_region_name = override_region_name

    if l_prefix:
        if not override_region_check:
            rig_region_name = 'L_leg'

        l_hip_name = hip.replace('<prefix>', 'L')
        de_rig_element(base_curve, rig_region_name.replace('<prefix>', 'L'), l_hip_name)

    if r_prefix:
        if not override_region_check:
            rig_region_name = 'R_leg'

        r_hip_name = hip.replace('<prefix>', 'R')
        de_rig_element(base_curve, rig_region_name.replace('<prefix>', 'R'), r_hip_name)

    if none_prefix:
        de_rig_element(base_curve, rig_region_name, hip)


    cmds.select(cl=True)


def ui_create_foot_rig():

    base_curve        = cmds.textField('jt_autorig_base_name_select_text', q=True, tx=True)
    l_prefix          = cmds.checkBox('jt_autorig_feet_rig_L', q=True, value=True)
    r_prefix          = cmds.checkBox('jt_autorig_feet_rig_R', q=True, value=True)
    arbitrary_prefix  = cmds.textField('jt_autorig_feet_rig_arbitrary', q=True, tx=True)
    ankle             = cmds.textField('jt_autorig_feet_ankle', q=True, tx=True)
    ik_ankle_ctl      = cmds.textField('jt_autorig_feet_ik_ankle_ctl', q=True, tx=True)
    reverse_lock_heel = cmds.textField('jt_autorig_feet_reverse_heel', q=True, tx=True)

    rig_region_name  = 'feet'

    toes = []

    for letter in ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
        if cmds.checkBox('jt_autorig_feet_toe_{0}_enable'.format(letter), q=True, value=True):
            toes.append([
                cmds.textField('jt_autorig_feet_toe_{0}_base_name'.format(letter), q=True, tx=True),
                cmds.checkBox('jt_autorig_feet_toe_{0}_reverse_lock_check'.format(letter), q=True, value=True),
                cmds.radioButton('jt_autorig_feet_toe_{0}_primary_radio'.format(letter), q=True, sl=True)
                ])

    prefixes = []
    if l_prefix: prefixes.append('L')
    if r_prefix: prefixes.append('R')
    if arbitrary_prefix != "":
        prefixes.append(arbitrary_prefix)
    for prefix in prefixes:
        create_foot_rig(base_curve, rig_region_name, ankle, ik_ankle_ctl, reverse_lock_heel, toes, prefix)


def ui_remove_foot_rig():
    base_curve = cmds.textField('jt_autorig_base_name_select_text', q=True, tx=True)
    l_prefix          = cmds.checkBox('jt_autorig_feet_rig_L', q=True, value=True)
    r_prefix          = cmds.checkBox('jt_autorig_feet_rig_R', q=True, value=True)
    arbitrary_prefix  = cmds.textField('jt_autorig_feet_rig_arbitrary', q=True, tx=True)

    rig_region_name  = 'feet'

    prefixes = []
    if l_prefix: prefixes.append('L')
    if r_prefix: prefixes.append('R')
    if arbitrary_prefix != "":
        prefixes.append(arbitrary_prefix)
    for prefix in prefixes:
        de_rig_element(base_curve, '{0}_{1}'.format(prefix, rig_region_name))


def ui_create_spine_rig():

    base_curve = cmds.textField('jt_autorig_base_name_select_text', q=True, tx=True) 
    pelvis  = cmds.textField('jt_autorig_pelvis_pelvis_select_text', q=True, tx=True)
    cog     = cmds.textField('jt_autorig_pelvis_cog_select_text', q=True, tx=True)
    spine_1 = cmds.textField('jt_autorig_pelvis_spine_1_select_text', q=True, tx=True)
    spine_2 = cmds.textField('jt_autorig_pelvis_spine_2_select_text', q=True, tx=True)
    spine_3 = cmds.textField('jt_autorig_pelvis_spine_3_select_text', q=True, tx=True)
    spine_4 = cmds.textField('jt_autorig_pelvis_spine_4_select_text', q=True, tx=True)
    neck    = cmds.textField('jt_autorig_pelvis_neck_select_text', q=True, tx=True)

    rig_region_name = 'spine'

    create_spine_rig(base_curve, rig_region_name, pelvis, cog, spine_1, spine_2, spine_3, spine_4, neck)


def ui_remove_spine_rig():

    base_curve = cmds.textField('jt_autorig_base_name_select_text', q=True, tx=True) 
    de_rig_element(base_curve, 'spine')


def ui_create_head_rig():

    base_curve = cmds.textField('jt_autorig_base_name_select_text', q=True, tx=True) 
    head    = cmds.textField('jt_autorig_head_head_select_text', q=True, tx=True)

    rig_region_name = 'head'

    create_head_rig(base_curve, rig_region_name, head)


def ui_remove_head_rig():

    base_curve = cmds.textField('jt_autorig_base_name_select_text', q=True, tx=True) 
    head    = cmds.textField('jt_autorig_head_head_select_text', q=True, tx=True)
    de_rig_element(base_curve, 'head', head)


#--------------------------------------------------------------------------------------------------
# rigging and de-rigging functions.
#--------------------------------------------------------------------------------------------------

def create_proxy_skeleton():
    pass


def create_skeleton_from_proxy():
    pass


def create_base_rig(cog, rig_region_name):
    # create curve and scale it to the correct size
    base_curve, base_curve_group = jt_ctl_curve.create(None, 'star_30')
    cmds.select(base_curve)
    cmds.setAttr(base_curve + '.scale', 5,5,5)
    cmds.makeIdentity(apply=True, t=0, r=1, s=1, n=0)

    # unparent the curve from the default group it is given so its a child of the world
    base_curve = cmds.rename('base')
    cmds.parent(w=True)
    cmds.select(base_curve_group, r=True)
    cmds.delete()

    # add a string attribute to keep track of all the nodes that are used for easy de-rigging
    # NOTE: text is stored in the attr as a string formatted like a python dict with the key being
    # the name of the body region and the value being a list of the nodes involved this makes 
    # de-rigging nice and easy as you just need to find the entry in the dict and delete all the nodes

    cmds.select(base_curve)
    cmds.addAttr(ln='rig_nodes', dt='string')
    cmds.setAttr(base_curve + '.rig_nodes', '{}', type='string')

    # add base_curve to base curve attr list
    add_node_to_rig_nodes(base_curve, 'base', base_curve)

    # update ui base_curve_field
    cmds.textField('jt_autorig_base_name_select_text', e=True, tx=base_curve)


def create_arm_rig(base_curve, rig_region_name, clavicle, shoulder, elbow, forearm, wrist, hand, side='L'):

    # create group to contain all rigging nodes
    cmds.select(cl=True)
    arm_group = cmds.group(em=True, n=rig_region_name + '_group')
    cmds.select(arm_group, base_curve, r=True)
    cmds.parent()

    # add the arm group node to the base curve rig nodes attr
    add_node_to_rig_nodes(base_curve, rig_region_name, arm_group)

    clavicle = change_prefix(clavicle, side)
    shoulder = change_prefix(shoulder, side)
    elbow    = change_prefix(elbow, side)
    forearm  = change_prefix(forearm, side)
    wrist    = change_prefix(wrist, side)
    hand     = change_prefix(hand, side)

    # add clavicle ctl
    clavicle_curve, clavicle_curve_group = jt_ctl_curve.create(clavicle, 'semicircle', True, True, True, True)
    cmds.select(clavicle_curve, r=True)

    if side == 'R':
        cmds.scale(1, 1, -1, r=True)
        cmds.makeIdentity(apply=True, t=0, r=1, s=1, n=0)
    cmds.rotate(-30,0,0, r=True, os=True)
    cmds.scale(1,1,1.8, r=True)
    cmds.makeIdentity(apply=True, t=0, r=1, s=1, n=0)

    # parent clavicle curve to arm group
    cmds.select(clavicle_curve_group, arm_group, r=True)
    cmds.parent()

    # add ik fk switch handle
    ik_fk_switch_curve, ik_fk_switch_curve_group = jt_ctl_curve.create(shoulder, 'paddle_2', True)
    if side == 'R':
        cmds.select(ik_fk_switch_curve, r=True)
        cmds.scale(1,-1,1, r=True)
        cmds.makeIdentity(apply=True, t=0, r=1, s=1, n=0)
    cmds.rotate(140, 0, 0, r=True, os=True)

    # parent ik fk switch curve to arm group
    cmds.select(ik_fk_switch_curve_group, arm_group, r=True)
    cmds.parent()

    add_keyable_attr(ik_fk_switch_curve, 'ik_fk_blend')
    cmds.setAttr(ik_fk_switch_curve + '.ik_fk_blend', 1)
    add_keyable_attr(ik_fk_switch_curve, 'ik_visibility', 'bool')
    add_keyable_attr(ik_fk_switch_curve, 'fk_visibility', 'bool')
    cmds.setAttr(ik_fk_switch_curve + '.fk_visibility', 1)
    add_keyable_attr(ik_fk_switch_curve, 'bone_visibility', 'bool')

    # duplicate joints for ik
    ik_shoulder = duplicate_joint_without_children(shoulder, '_ik')
    ik_elbow    = duplicate_joint_without_children(elbow   , '_ik')
    ik_wrist    = duplicate_joint_without_children(wrist   , '_ik')
    ik_hand     = duplicate_joint_without_children(hand    , '_ik')

    # rebuild ik bones
    cmds.select(ik_hand, ik_wrist, r=True)
    cmds.parent()

    cmds.select(ik_wrist, ik_elbow, r=True)
    cmds.parent()

    cmds.select(ik_elbow, ik_shoulder, r=True)
    cmds.parent()

    # duplicate joints for fk
    fk_shoulder = duplicate_joint_without_children(shoulder, '_fk')
    fk_elbow    = duplicate_joint_without_children(elbow   , '_fk')
    fk_wrist    = duplicate_joint_without_children(wrist   , '_fk')
    fk_hand     = duplicate_joint_without_children(hand    , '_fk')

    # rebuild fk bones
    cmds.select(fk_wrist, r=True)
    cmds.select(fk_elbow, add=True)
    cmds.parent()

    cmds.select(fk_elbow, fk_shoulder, r=True)
    cmds.parent()

    cmds.select(fk_hand, fk_wrist, r=True)
    cmds.parent()

    # parent constrain ik and fk bones to skeleton
    cmds.select(ik_shoulder, r=True)
    ik_shoulder_group = cmds.group(n=side + '_ik_arm_bones')
    cmds.select(clavicle, ik_shoulder_group, r=True)
    cmds.parentConstraint(mo=True, weight=1)
    cmds.scaleConstraint(mo=True, weight=1)

    cmds.select(fk_shoulder, r=True)
    fk_shoulder_group = cmds.group(n=side + '_fk_arm_bones')
    cmds.select(clavicle, fk_shoulder_group, r=True)
    cmds.parentConstraint(mo=True, weight=1)
    cmds.scaleConstraint(mo=True, weight=1)

    # parent ik and fk bones to arm group
    cmds.select(ik_shoulder_group, arm_group, r=True)
    cmds.parent()
    cmds.select(fk_shoulder_group, arm_group, r=True)
    cmds.parent()

    # conect up new bones visibility attrs to ctl curves
    cmds.connectAttr(ik_fk_switch_curve + '.bone_visibility', ik_shoulder_group + '.visibility', f=True)
    cmds.connectAttr(ik_fk_switch_curve + '.bone_visibility', fk_shoulder_group + '.visibility', f=True)

    # connect up blending to attrs in handle
    shoulder_blend = create_blend(ik_shoulder + '.rotate', fk_shoulder + '.rotate', shoulder + '.rotate', ik_fk_switch_curve + '.ik_fk_blend')
    elbow_blend    = create_blend(ik_elbow + '.rotate', fk_elbow + '.rotate', elbow + '.rotate', ik_fk_switch_curve + '.ik_fk_blend')
    wrist_blend = create_blend(ik_wrist + '.rotate', fk_wrist + '.rotate', wrist + '.rotate', ik_fk_switch_curve + '.ik_fk_blend')

    # add blend nodes to base curve rig nodes attr
    add_node_to_rig_nodes(base_curve, rig_region_name, (shoulder_blend, elbow_blend, wrist_blend))

    # create ik rp solver
    cmds.select(ik_shoulder + '.rotatePivot', ik_wrist + '.rotatePivot', r=True)
    ik_handle, ik_effector = cmds.ikHandle(sol='ikRPsolver')
    cmds.connectAttr(ik_fk_switch_curve + '.bone_visibility', ik_handle + '.visibility', force=True)

    # add ik handle to arm group 
    cmds.select(ik_handle, arm_group, r=True)
    cmds.parent()

    # create ik controlls
    ik_hand_ctl, ik_hand_ctl_group = jt_ctl_curve.create(ik_wrist, 'diamond', False, align=True, lock_unused=False)
    cmds.connectAttr(ik_fk_switch_curve + '.ik_visibility', ik_hand_ctl_group + '.visibility', force=True)
    cmds.select(ik_hand_ctl, ik_wrist, r=True)
    cmds.parentConstraint(mo=True, skipTranslate=('x','y','z'), weight=1)
    cmds.scaleConstraint(mo=True, weight=1)

    cmds.select(ik_hand_ctl, r=True)
    cmds.scale(0.6, 0.6, 0.6, r=True)
    cmds.makeIdentity(apply=True, t=0, r=1, s=1, n=0)

    cmds.select(ik_hand_ctl, ik_handle, r=True)
    cmds.parentConstraint(mo=True, weight=1)

    pole_vector_ctl, pole_vector_ctl_group = jt_ctl_curve.create(ik_elbow, 'cube', False, align=False, lock_unused=False)
    cmds.connectAttr(ik_fk_switch_curve + '.ik_visibility', pole_vector_ctl_group + '.visibility', f=True)
    cmds.select(pole_vector_ctl, ik_handle, r=True)
    cmds.poleVectorConstraint(weight=1)

    cmds.select(pole_vector_ctl, r=True)
    cmds.scale(0.2, 0.2, 0.2, r=True)
    cmds.makeIdentity(apply=True, t=0, r=1, s=1, n=0)

    # add ik ctl curves to arm group 
    cmds.select(ik_hand_ctl_group, arm_group, r=True)
    cmds.parent()
    cmds.select(pole_vector_ctl_group, arm_group, r=True)
    cmds.parent()

    # add fk controll curves
    for item in ((fk_shoulder, 'circle'), (fk_elbow, 'circle'), (fk_wrist, 'circle')):
        ctl_curve, ctl_group = jt_ctl_curve.create(item[0], item[1], True, True, True, True)
        cmds.connectAttr(ik_fk_switch_curve + '.fk_visibility', ctl_group + '.visibility', f=True)

        # add ik handle to arm group 
        cmds.select(ctl_group, arm_group, r=True)
        cmds.parent()

    # hook up forearm split
    forearm_split_multiply_node = cmds.createNode('multiplyDivide', n=forearm + '_split')
    cmds.setAttr(forearm_split_multiply_node + '.input2', 0.5, 0.5, 0.5)
    cmds.connectAttr(wrist + '.rotate', forearm_split_multiply_node + '.input1', f=True)
    cmds.connectAttr(forearm_split_multiply_node + '.output.outputY', forearm + '.rotate.rotateY', force=True)

    # add forearm multiply node to base curve attr list
    add_node_to_rig_nodes(base_curve, rig_region_name, forearm_split_multiply_node)


def create_leg_rig(base_curve, rig_region_name, pelvis, hip, knee, ankle, prefix):

    rig_region_name = rig_region_name.replace('<prefix>', prefix)

    # create group to contain all rigging nodes
    cmds.select(cl=True)
    leg_group = cmds.group(em=True, n=rig_region_name + '_group')
    cmds.select(leg_group, base_curve, r=True)
    cmds.parent()

    # add the leg group node to the base curve rig nodes attr
    add_node_to_rig_nodes(base_curve, rig_region_name, leg_group)

    pelvis             = pelvis.replace('<prefix>', prefix)
    hip                = hip.replace('<prefix>', prefix)
    knee               = knee.replace('<prefix>', prefix)
    ankle              = ankle.replace('<prefix>', prefix)

    # add ik/fk switch handle
    ik_fk_switch_curve, ik_fk_switch_group = jt_ctl_curve.create(hip, 'paddle_3', True)
    cmds.select(ik_fk_switch_curve)
    cmds.rotate(90,0,90, os=True)
    if prefix == 'R':
        cmds.scale(1,1,-1, r=True)
    cmds.makeIdentity(apply=True, t=0, r=1, s=1, n=0)

    # parent ik_fk_switch_group to leg group
    cmds.select(ik_fk_switch_group, leg_group, r=True)
    cmds.parent()

    add_keyable_attr(ik_fk_switch_curve, 'ik_fk_blend')
    add_keyable_attr(ik_fk_switch_curve, 'ik_visibility', 'bool')
    cmds.setAttr(ik_fk_switch_curve + '.ik_visibility', 1)
    add_keyable_attr(ik_fk_switch_curve, 'fk_visibility', 'bool')
    add_keyable_attr(ik_fk_switch_curve, 'bone_visibility', 'bool')

    # duplicate joints for ik
    ik_hip   = duplicate_joint_without_children(hip, '_ik')
    ik_knee  = duplicate_joint_without_children(knee, '_ik')
    ik_ankle = duplicate_joint_without_children(ankle, '_ik')

    # duplicate joints for fk
    fk_hip   = duplicate_joint_without_children(hip, '_fk')
    fk_knee  = duplicate_joint_without_children(knee, '_fk')
    fk_ankle = duplicate_joint_without_children(ankle, '_fk')

    # rebuild ik joints
    cmds.select(ik_knee, ik_hip, r=True)
    cmds.parent()
    cmds.select(ik_ankle, ik_knee, r=True)
    cmds.parent()

    # rebuild fk joints
    cmds.select(fk_knee, fk_hip, r=True)
    cmds.parent()
    cmds.select(fk_ankle, fk_knee, r=True)
    cmds.parent()

    # parent constrain ik and fk bones to skeleton
    cmds.select(ik_hip, r=True)
    ik_hip_group = cmds.group(n=rig_region_name + '_ik_leg_bones')
    cmds.select(pelvis, ik_hip_group, r=True)
    cmds.parentConstraint(mo=True, weight=1)
    cmds.scaleConstraint(mo=True, weight=1)
    cmds.connectAttr(ik_fk_switch_curve + '.bone_visibility', ik_hip_group + '.visibility', f=True)

    cmds.select(fk_hip, r=True)
    fk_hip_group = cmds.group(n=rig_region_name + '_fk_leg_bones')
    cmds.select(pelvis, fk_hip_group, r=True)
    cmds.parentConstraint(mo=True, weight=1)
    cmds.scaleConstraint(mo=True, weight=1)
    cmds.connectAttr(ik_fk_switch_curve + '.bone_visibility', fk_hip_group + '.visibility', f=True)

    # parent ik_hip_group and fk_hip_group to leg group
    cmds.select([ik_hip_group, fk_hip_group], leg_group, r=True)
    cmds.parent()

    # connect up blending to attrs in handle
    hip_blend = create_blend(ik_hip + '.rotate', fk_hip + '.rotate', hip + '.rotate', ik_fk_switch_curve + '.ik_fk_blend')
    knee_blend = create_blend(ik_knee + '.rotate', fk_knee + '.rotate', knee + '.rotate', ik_fk_switch_curve + '.ik_fk_blend')
    ankle_blend = create_blend(ik_ankle + '.rotate', fk_ankle + '.rotate', ankle + '.rotate', ik_fk_switch_curve + '.ik_fk_blend')

    # add blend nodes to base curve rig nodes attr
    add_node_to_rig_nodes(base_curve, rig_region_name, (hip_blend, knee_blend, ankle_blend))

    # create ik ankle ctl curve
    ik_ankle_curve, ik_ankle_curve_group = jt_ctl_curve.create(ik_ankle, 'diamond', False, lock_unused=False)
    cmds.setAttr(ik_ankle_curve + '.scale', 0.5, 0.5, 0.5)
    cmds.makeIdentity(ik_ankle_curve, apply=True, t=0, r=1, s=1, n=0)
    cmds.connectAttr(ik_fk_switch_curve + '.ik_visibility', ik_ankle_curve_group + '.visibility', f=True)


    # parent ik ik_ankle ctl to leg group
    cmds.select(ik_ankle_curve_group, leg_group, r=True)
    cmds.parent()

    # create ik handles for leg
    cmds.select(ik_hip + '.rotatePivot', ik_ankle + '.rotatePivot', r=True)
    hip_ankle_ik_handle, hip_ankle_ik_effector = cmds.ikHandle(sol='ikRPsolver')
    cmds.connectAttr(ik_fk_switch_curve + '.bone_visibility', hip_ankle_ik_handle + '.visibility', force=True)

    # parent_ik_handle to ik_ankls group
    cmds.select(hip_ankle_ik_handle, leg_group, r=True)
    cmds.parent()

    # constrain ik ankle to ankle ctl
    cmds.select(ik_ankle_curve, hip_ankle_ik_handle)
    cmds.parentConstraint(mo=True, weight=1)
    cmds.scaleConstraint(mo=True, weight=1)

    # create pole vecotor ctl
    pole_vector_curve, pole_vector_curve_group = jt_ctl_curve.create(ik_knee, 'cube', False, lock_unused=False)
    cmds.select(pole_vector_curve, r=True)
    cmds.setAttr(pole_vector_curve + '.scale', 0.2, 0.2, 0.2)
    cmds.makeIdentity(apply=True, t=0, r=1, s=1, n=0)
    cmds.select(pole_vector_curve, hip_ankle_ik_handle, r=True)
    cmds.poleVectorConstraint(weight=1)
    cmds.connectAttr(ik_fk_switch_curve + '.ik_visibility', pole_vector_curve_group + '.visibility', f=True)

    # parent ik pole vector ctl to leg group
    cmds.select(pole_vector_curve_group, leg_group, r=True)
    cmds.parent()

    # add fk controll curves
    for item in ((fk_hip, 'circle'), (fk_knee, 'circle')):
        ctl_curve, ctl_curve_group = jt_ctl_curve.create(item[0], item[1], True, True, True, True)
        cmds.connectAttr(ik_fk_switch_curve + '.fk_visibility', ctl_curve_group + '.visibility', f=True)

        # parent ctl_curve_group to leg group
        cmds.select(ctl_curve_group, leg_group, r=True)
        cmds.parent()

    fk_ankle_curve, fk_ankle_curve_group = jt_ctl_curve.create(fk_ankle, 'circle', True, True, True, True)
    cmds.connectAttr(ik_fk_switch_curve + '.fk_visibility', fk_ankle_curve_group + '.visibility', f=True)   
    cmds.select(fk_ankle_curve, r=True)
    cmds.setAttr(fk_ankle_curve + '.rotate', 50, 0, 0)
    cmds.makeIdentity(apply=True, t=0, r=1, s=1, n=0)

    # parent fk controlls to leg group
    cmds.select(fk_ankle_curve_group, leg_group, r=True)
    cmds.parent()







def create_foot_rig(base_curve, rig_region_name, ankle, ik_ankle_ctl, reverse_lock_heel, toes, prefix):

    rig_region_name = prefix + '_' + rig_region_name

    # create group to contain all rigging nodes
    cmds.select(cl=True)
    foot_group = cmds.group(em=True, n=rig_region_name + '_group')
    cmds.select(foot_group, base_curve, r=True)
    cmds.parent()

    # add the leg group node to the base curve rig nodes attr
    add_node_to_rig_nodes(base_curve, rig_region_name, foot_group)

    ankle                = ankle.replace('<prefix>', prefix)
    ik_ankle_ctl         = ik_ankle_ctl.replace('<prefix>', prefix)
    reverse_lock_heel    = reverse_lock_heel.replace('<prefix>', prefix)
    toes                 = [[toe[0].replace('<prefix>', prefix), toe[1], toe[2]] for toe in toes]

    # create dict of orphan bones
    bone_copies = {}
    for section_name in ['fk', 'rl', 'rl_target']: # rl = reverse lock
        bones = []
        for toe in toes:
            if toe[1] or section_name == 'fk' or section_name == 'rl': # skip non reverse lock for reverse lock target boens
                toe_chain = []
                for toe_num in ['1', '2', '3', '4']:
                    toe_name = toe[0].replace('1', toe_num)
                    toe_copy = duplicate_joint_without_children(toe_name, '_{0}'.format(section_name))
                    toe_chain.append([toe_name, toe_copy]) # [original_bone_name, new bone name]
                bones.append(
                    {
                        'chain'   : toe_chain,
                        'reverse' : toe[1],
                        'primary' : toe[2]
                    })
            bone_copies[section_name] = bones

    # rebuild 2 sets of fk bones
    # these are the bones that will later be blended 
    for section_name in ['fk', 'rl']:
        # create duplicate ankle joint
        ankle_copy = duplicate_joint_without_children(ankle, '_{0}'.format(section_name))
        # add ankle to dict
        bone_copies['ankle_{0}'.format(section_name)] = ankle_copy
        # parent heirarchy to foot group
        cmds.select(ankle_copy, foot_group, r=True)
        cmds.parent()
        for toe_chain in bone_copies[section_name]:
            parent_bone = ankle_copy
            for bone in toe_chain['chain']:
                cmds.select(bone[1], parent_bone, r=True)
                cmds.parent()
                parent_bone = bone[1]


    # rebuild reverse lock target bones
    section_name = 'rl_target'
    target_ankle_copy = duplicate_joint_without_children(ankle, '_{0}'.format(section_name))
    target_heel_copy = duplicate_joint_without_children(reverse_lock_heel, '_{0}'.format(section_name))
    # add new bones to dict
    bone_copies['ankle_rl_target'] = target_ankle_copy
    bone_copies['heel_rl_target'] = target_heel_copy
    bone_copies['primary_toe_rl_target'] = None

    for toe_chain in bone_copies[section_name]:
        if toe_chain['reverse']:
            bone_copies['primary_toe_rl_target'] = toe[0]
            parent_bone = target_heel_copy
            reverse_toe_chain = toe_chain['chain']
            reverse_toe_chain.reverse()
            for bone in reverse_toe_chain:
                cmds.select(bone[1], parent_bone, r=True)
                cmds.parent()
                parent_bone = bone[1] 

            if toe_chain['primary']:
                cmds.select(target_ankle_copy, parent_bone, r=True)
                cmds.parent()

    # create reverse lock foot control
    rl_foot_ctl, rl_foot_group = jt_ctl_curve.create(bone_copies['heel_rl_target'], 'square', lock_unused=False)

    # move the foot controll to a more sensible place
    cmds.setAttr(rl_foot_ctl + '.rotateX', 90)
    cmds.setAttr(rl_foot_ctl + '.scaleZ', 1.5)
    cmds.select(rl_foot_ctl, r=True)
    cmds.makeIdentity(apply=True, t=1, r=1, s=1, n=0)

    # parent everything to foot ctl
    cmds.select(rl_foot_group, foot_group, r=True)
    cmds.parent()
    # put reverse foot ctl under a group to allow for rotation
    cmds.select(bone_copies['heel_rl_target'], r=True)
    reverse_lock_group = cmds.group()
    cmds.select(reverse_lock_group, foot_group, r=True)
    cmds.parent()
    # parent rl foot ctl group to foot group
    cmds.select(rl_foot_ctl, reverse_lock_group, r=True)
    cmds.parentConstraint(mo=True, weight=1)
    cmds.scaleConstraint(mo=True, weight=1)

    # add rl foot control attribs
    generic_attrs = [
        'master_roll', 
        'master_spread', 
        'heel_pivot', 
        'toe_base_break',
        'toe_mid_1_break',
        'toe_mid_2_break',
        'toe_end_break',
        'toe_base_springback'
        ]

    per_toe_attrs = [
        'roll_mult', 
        'spread', 
        'toe_base',
        'toe_mid_1',
        'toe_mid_2',
        'toe_end']

    # add generic foor attrs
    add_label_attr(rl_foot_ctl, 'generic_attributes')
    for attr in generic_attrs:
        add_keyable_attr(rl_foot_ctl, attr, type='float')

    # and initialise sensibly:
    cmds.setAttr(rl_foot_ctl + '.toe_base_break',      5)
    cmds.setAttr(rl_foot_ctl + '.toe_mid_1_break',     20)
    cmds.setAttr(rl_foot_ctl + '.toe_mid_2_break',     25)
    cmds.setAttr(rl_foot_ctl + '.toe_end_break',       50)
    cmds.setAttr(rl_foot_ctl + '.toe_base_springback', 20)

    # add per toe attrs
    for toe in bone_copies['rl_target']: 
        if toe['reverse']:
            toe_name = toe['chain'][0][0][0:-2]
            add_label_attr(rl_foot_ctl, toe_name)
            for attr in per_toe_attrs:
                add_keyable_attr(rl_foot_ctl, '{0}_{1}'.format(attr, toe_name), type='float')
                # initialise roll mult to 1
                if attr == 'roll_mult':
                    cmds.setAttr('{0}.{1}_{2}'.format(rl_foot_ctl, attr, toe_name), 1)



    #                             * Ankle
    #                            /
    #                           /
    #                          /
    # 4      3      2       1 /
    #  *______*______*_______*  
    #   \_______________________* Heel






    # toe 1 break                     _____________________________
    # toe end break _________________/_________/________/_________



    # heel.y = heel_pivot
    # heel.z = clamp(master_roll, 0, 180)


    # hook up generic attributes 
    cmds.connectAttr(rl_foot_ctl + '.heel_pivot', bone_copies['heel_rl_target'] + '.rotateZ')
    heel_roll_attr, heel_roll_nodes = comp.Clamp(rl_foot_ctl + '.master_roll', -90, 0).compile()
    cmds.connectAttr(heel_roll_attr, bone_copies['heel_rl_target'] + '.rotateX')
    for node in heel_roll_nodes:
        add_node_to_rig_nodes(base_curve, rig_region_name, node)


    # hook up undividtal toes
    for toe in bone_copies['rl_target']: 
        if toe['reverse']:
            toe_name = toe['chain'][0][0][0:-2]



            toe_end_attr, toe_end_nodes = comp.Clamp(
                                                comp.Minus(
                                                    comp.Minus(
                                                        comp.Minus(
                                                            rl_foot_ctl + '.master_roll', 
                                                            rl_foot_ctl + '.toe_mid_1_break'), 
                                                        rl_foot_ctl + '.toe_base_break'),
                                                    rl_foot_ctl + '.toe_mid_2_break'),
                                                0, 
                                                rl_foot_ctl + '.toe_end_break').compile()

            cmds.connectAttr(toe_end_attr, toe['chain'][0][1] + '.rotateX')


            toe_mid_1_attr, toe_mid_1_nodes = comp.Clamp(
                                                    comp.Minus(
                                                        comp.Minus(
                                                            rl_foot_ctl + '.master_roll', 
                                                            rl_foot_ctl + '.toe_mid_2_break'),
                                                        rl_foot_ctl + '.toe_base_break'),
                                                    0, 
                                                    rl_foot_ctl + '.toe_mid_1_break').compile()

            cmds.connectAttr(toe_mid_1_attr, toe['chain'][1][1] + '.rotateX')


            toe_mid_2_attr, toe_mid_2_nodes = comp.Clamp(
                                                    comp.Minus(
                                                        rl_foot_ctl + '.master_roll', 
                                                        rl_foot_ctl + '.toe_base_break'), 
                                                    0, 
                                                    rl_foot_ctl + '.toe_mid_2_break').compile()

            cmds.connectAttr(toe_mid_2_attr, toe['chain'][2][1] + '.rotateX')


            toe_base_attr, toe_base_nodes = comp.Minus(
                                                    comp.Clamp( 
                                                        rl_foot_ctl + '.master_roll', 
                                                        0, 
                                                        rl_foot_ctl + '.toe_base_break'),
                                                    comp.Clamp(
                                                        comp.Minus(
                                                            rl_foot_ctl + '.master_roll',
                                                            rl_foot_ctl + '.toe_base_springback'),
                                                        0, 
                                                        30)).compile()

            cmds.connectAttr(toe_base_attr, toe['chain'][3][1] + '.rotateX')




            for node in toe_end_nodes + toe_mid_1_nodes + toe_mid_2_nodes + toe_base_nodes:
                add_node_to_rig_nodes(base_curve, rig_region_name, node)


            # for i, joint in enumerate(toe['chain']):
            #     joint_name = joint[1]

            #     # clamp joint 4

            #     cmds.connectAttr(rl_foot_ctl + '.master_roll', joint_name + '.rotateX')




        # 'toe_base_break',
        # 'toe_mid_1_break',
        # 'toe_mid_2_break',
        # 'toe_end_break', 






def create_spine_rig(base_curve, rig_region_name, pelvis, cog, spine_1, spine_2, spine_3, spine_4, neck):

    # create group to contain all rigging nodes
    cmds.select(cl=True)
    spine_group = cmds.group(em=True, n=rig_region_name + '_group')
    cmds.select(spine_group, base_curve, r=True)
    cmds.parent()

    # add the arm group node to the base curve rig nodes attr
    add_node_to_rig_nodes(base_curve, rig_region_name, spine_group)

    cog_curve, cog_curve_group = jt_ctl_curve.create(cog, 'star_5', lock_unused=False)
    cmds.setAttr(cog_curve + '.scale', 3,3,3)
    cmds.select(cog_curve, r=True)
    cmds.makeIdentity(apply=True, t=0, r=0, s=1, n=0)

    cmds.select(cog_curve, cog, r=True)
    cmds.parentConstraint(mo=True, weight=1)
    cmds.scaleConstraint(mo=True, weight=1)

    cmds.select(cog_curve_group, base_curve, r=True)
    cmds.parent()

    pelvis_curve, pelvis_curve_group = jt_ctl_curve.create(pelvis, 'waist', True, True, True, True)
    spine_1_curve, spine_1_curve_group = jt_ctl_curve.create(spine_1, 'circle', True, True, True, True)
    spine_2_curve, spine_2_curve_group = jt_ctl_curve.create(spine_2, 'circle', True, True, True, True)
    spine_3_curve, spine_3_curve_group = jt_ctl_curve.create(spine_3, 'circle', True, True, True, True)
    spine_4_curve, spine_4_curve_group = jt_ctl_curve.create(spine_4, 'circle', True, True, True, True)
    neck_curve, neck_curve_group = jt_ctl_curve.create(neck, 'circle', True, True, True, True)

    # parent fk controlls to spine group
    cmds.select(cog_curve_group, pelvis_curve_group, spine_1_curve_group, spine_2_curve_group, spine_3_curve_group, spine_4_curve_group, neck_curve_group, spine_group, r=True)
    cmds.parent()


def create_head_rig(base_curve, rig_region_name, head):

    # create group to contain all rigging nodes
    cmds.select(cl=True)
    head_group = cmds.group(em=True, n=rig_region_name + '_group')
    cmds.select(head_group, base_curve, r=True)
    cmds.parent()

    # add the arm group node to the base curve rig nodes attr
    add_node_to_rig_nodes(base_curve, rig_region_name, head_group)

    head_curve, head_curve_group = jt_ctl_curve.create(head, 'circle', True, True, True, True)  
    cmds.select(head_curve, r=True)
    cmds.setAttr(head_curve + '.scale', 1,1,1)
    cmds.makeIdentity(apply=True, t=0, r=1, s=1, n=0)

    cmds.select(head_curve_group, head_group, r=True)
    cmds.parent()


def create_finger_rig(base_curve, finger_name, hand_group, rig_region_name, hand_curve, base_joint, side):

    top_bone = base_joint
    mid_bone = base_joint[:-1] + '2'
    end_bone = base_joint[:-1] + '3'

    # create empty group to store hand controll attrs
    finger_group = cmds.group(em=True, n=side + '_' + finger_name + '_group')
    cmds.select(finger_group, hand_group, r=True)
    cmds.parent()

    # add attrs to group
    attr_list = ['mid_mult', 'end_mult', 'roll', 'spread', 'spread_in', 'spread_mult', 'fist', 'curl', 'top', 'mid', 'end', 'damp']

    for i in range(len(attr_list)):
        add_keyable_attr(finger_group, attr_list[i], type='float')

    # create utility nodes
    # sum fist and curl
    fist_curl_sum_node = cmds.createNode('plusMinusAverage', n=finger_name + '_fist_curl_sum')
    add_node_to_rig_nodes(base_curve, rig_region_name, fist_curl_sum_node)

    cmds.connectAttr(finger_group + '.' + attr_list[6], fist_curl_sum_node + '.input1D[0]', f=True)
    cmds.connectAttr(finger_group + '.' + attr_list[7], fist_curl_sum_node + '.input1D[1]', f=True)

    # attenuate fist and curl value with mid_mult and end_mult
    finger_adjust_mult = cmds.createNode('multiplyDivide', n=finger_name + '_finger_adjust')
    add_node_to_rig_nodes(base_curve, rig_region_name, finger_adjust_mult)

    cmds.setAttr(finger_adjust_mult + '.input1.input1X', 1)
    cmds.connectAttr(finger_group + '.' + attr_list[0], finger_adjust_mult + '.input1.input1Y', f=True)
    cmds.connectAttr(finger_group + '.' + attr_list[1], finger_adjust_mult + '.input1.input1Z', f=True)

    cmds.connectAttr(fist_curl_sum_node + '.output1D', finger_adjust_mult + '.input2X', f=True)
    cmds.connectAttr(fist_curl_sum_node + '.output1D', finger_adjust_mult + '.input2Y', f=True)
    cmds.connectAttr(fist_curl_sum_node + '.output1D', finger_adjust_mult + '.input2Z', f=True)

    # sum single joints with fist and curl
    individual_curl_sum_node = cmds.createNode('plusMinusAverage', n=finger_name + '_individual_curl_sum')
    add_node_to_rig_nodes(base_curve, rig_region_name, individual_curl_sum_node)

    cmds.connectAttr(finger_adjust_mult + '.output', individual_curl_sum_node + '.input3D[0]', f=True)
    cmds.connectAttr(finger_group + '.' + attr_list[8], individual_curl_sum_node + '.input3D[1].input3Dx', f=True)
    cmds.connectAttr(finger_group + '.' + attr_list[9], individual_curl_sum_node + '.input3D[1].input3Dy', f=True)
    cmds.connectAttr(finger_group + '.' + attr_list[10], individual_curl_sum_node + '.input3D[1].input3Dz', f=True)

    # sum spread_in and spread
    spread_sum_node = cmds.createNode('plusMinusAverage', n=finger_name + '_spread_curl_sum')
    add_node_to_rig_nodes(base_curve, rig_region_name, spread_sum_node)

    cmds.connectAttr(finger_group + '.' + attr_list[3], spread_sum_node + '.input1D[0]', f=True)
    cmds.connectAttr(finger_group + '.' + attr_list[4], spread_sum_node + '.input1D[1]', f=True)

    # attenuate spread based on spread_mult
    spread_mult_node = cmds.createNode('multiplyDivide', n=finger_name + '_finger_adjust')
    add_node_to_rig_nodes(base_curve, rig_region_name, spread_mult_node)

    cmds.connectAttr(spread_sum_node + '.output1D', spread_mult_node + '.input1X')
    cmds.connectAttr(finger_group + '.' + attr_list[5], spread_mult_node + '.input2X', f=True)

    # attenuate rotations, useful for thumb damp etc
    damp_node = cmds.createNode('multiplyDivide', n=finger_name + '_damp')
    add_node_to_rig_nodes(base_curve, rig_region_name, damp_node)

    cmds.setAttr(finger_group + '.' + attr_list[11], 1)
    cmds.connectAttr(individual_curl_sum_node + '.output3D', damp_node + '.input1', f=True)
    cmds.connectAttr(finger_group + '.' + attr_list[11], damp_node + '.input2X', f=True)
    cmds.connectAttr(finger_group + '.' + attr_list[11], damp_node + '.input2Y', f=True)
    cmds.connectAttr(finger_group + '.' + attr_list[11], damp_node + '.input2Z', f=True)

    # connect up output to bones
    cmds.connectAttr(damp_node + '.outputX', top_bone + '.rotateX', f=True)
    cmds.connectAttr(damp_node + '.outputY', mid_bone + '.rotateX', f=True)
    cmds.connectAttr(damp_node + '.outputZ', end_bone + '.rotateX', f=True)
    cmds.connectAttr(spread_mult_node + '.outputX', top_bone + '.rotateZ', f=True)
    cmds.connectAttr(finger_group + '.' + attr_list[2], top_bone + '.rotateY', f=True)

    return finger_group


def create_hand_rig(base_curve, rig_region_name, hand, ring_cup, pinky_cup, thumb_base, index_base, middle_base, ring_base, pinky_base, side):

    # create group to contain all rigging nodes
    cmds.select(cl=True)
    hand_group = cmds.group(em=True, n=rig_region_name + '_group')
    cmds.select(hand_group, base_curve, r=True)
    cmds.parent()

    # add the arm group node to the base curve rig nodes attr
    add_node_to_rig_nodes(base_curve, rig_region_name, hand_group)

    # rename bone names to correspond with side
    hand        = change_prefix(hand, side)
    ring_cup    = change_prefix(ring_cup, side)
    pinky_cup   = change_prefix(pinky_cup, side)
    thumb_base  = change_prefix(thumb_base, side)
    index_base  = change_prefix(index_base, side)
    middle_base = change_prefix(middle_base, side)
    ring_base   = change_prefix(ring_base, side)
    pinky_base  = change_prefix(pinky_base, side)

    # create hand control curve
    hand_curve, hand_curve_group = jt_ctl_curve.create(hand, 'paddle', True)
    cmds.select(hand_curve)
    cmds.setAttr(hand_curve + '.rotate', -90,0,0)
    cmds.makeIdentity(apply=True, t=0, r=1, s=1, n=0)
    if side == 'R':
        cmds.setAttr(hand_curve + '.scale', 1,1,-1)
        cmds.makeIdentity(apply=True, t=0, r=1, s=1, n=0)

    # parent hand control group to hand group
    cmds.select(hand_curve_group, hand_group, r=True)
    cmds.parent()

    # add generic attrs to curve
    attr_list = ['mid_mult', 'end_mult', 'master_spread', 'fist', 'ring_cup' , 'pinky_cup', 'thumb_damp']

    # rig all the fingers
    finger_list           = [thumb_base, index_base, middle_base, ring_base, pinky_base]
    finger_base_name_list = ['thumb', 'index', 'middle', 'ring', 'pinky']
    finger_rig_list       = [0,0,0,0,0]
    for i in range(len(finger_list)):
        finger_rig_list[i] = create_finger_rig(base_curve, finger_base_name_list[i], hand_group, rig_region_name, hand_curve, finger_list[i], side)

    for i in range(len(attr_list)):
        add_keyable_attr(hand_curve, attr_list[i], type='float')

    # set mid and end mult attrs
    cmds.setAttr(hand_curve + '.' + attr_list[0], 1.3)
    cmds.setAttr(hand_curve + '.' + attr_list[1], 1.1)

    # connnect up cup attrs
    cmds.connectAttr(hand_curve + '.' + attr_list[4], ring_cup + '.rotateX', f=True)
    cmds.connectAttr(hand_curve + '.' + attr_list[5], pinky_cup + '.rotateX', f=True)

    # hook up spread attributes
    cmds.setAttr(finger_rig_list[0] + '.spread_mult', 2)
    cmds.setAttr(finger_rig_list[1] + '.spread_mult', 1)
    cmds.setAttr(finger_rig_list[2] + '.spread_mult', 0)
    cmds.setAttr(finger_rig_list[3] + '.spread_mult', -1)
    cmds.setAttr(finger_rig_list[4] + '.spread_mult', -2)

    # create and hook upfinger curl attributes 
    add_label_attr(hand_curve, 'finger_curl')
    for i in range(len(finger_list)):
        curl_attr = finger_base_name_list[i] + '_curl'
        add_keyable_attr(hand_curve, curl_attr)
        cmds.connectAttr(hand_curve + '.' + curl_attr, finger_rig_list[i] + '.curl')

    # set up thumb_damp attr
    cmds.setAttr(hand_curve + '.' + attr_list[6], 0.4)
    cmds.connectAttr(hand_curve + '.' + attr_list[6], finger_rig_list[0] + '.damp')

    # create and hook up per finger attributes 
    for i in range(len(finger_list)):
        spread_attr = finger_base_name_list[i] + '_spread'
        roll_attr   = finger_base_name_list[i] + '_roll'
        top_attr    = finger_base_name_list[i] + '_top'
        mid_attr    = finger_base_name_list[i] + '_mid'
        end_attr    = finger_base_name_list[i] + '_end'

        add_label_attr(hand_curve, finger_base_name_list[i])

        add_keyable_attr(hand_curve, spread_attr)
        add_keyable_attr(hand_curve, roll_attr)
        add_keyable_attr(hand_curve, top_attr)
        add_keyable_attr(hand_curve, mid_attr)
        add_keyable_attr(hand_curve, end_attr)

        cmds.connectAttr(hand_curve + '.' + attr_list[3], finger_rig_list[i] + '.fist')
        cmds.connectAttr(hand_curve + '.' + attr_list[2], finger_rig_list[i] + '.spread_in')

        cmds.connectAttr(hand_curve + '.' + attr_list[0], finger_rig_list[i] + '.mid_mult')
        cmds.connectAttr(hand_curve + '.' + attr_list[1], finger_rig_list[i] + '.end_mult')

        cmds.connectAttr(hand_curve + '.' + spread_attr, finger_rig_list[i] + '.spread')
        cmds.connectAttr(hand_curve + '.' + roll_attr,   finger_rig_list[i] + '.roll')
        cmds.connectAttr(hand_curve + '.' + top_attr,    finger_rig_list[i] + '.top')
        cmds.connectAttr(hand_curve + '.' + mid_attr,    finger_rig_list[i] + '.mid')
        cmds.connectAttr(hand_curve + '.' + end_attr,    finger_rig_list[i] + '.end')

