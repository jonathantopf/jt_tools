
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



#--------------------------------------------------------------------------------------------------
# ui functions.
#--------------------------------------------------------------------------------------------------

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

    base_curve = cmds.textField('jt_autorig_base_name_select_text', q=True, tx=True)
    pelvis             = cmds.textField('jt_autorig_legs_pelvis_select_text', q=True, tx=True)
    hip                = cmds.textField('jt_autorig_legs_hip_select_text', q=True, tx=True)
    knee               = cmds.textField('jt_autorig_legs_knee_select_text', q=True, tx=True)
    ankle              = cmds.textField('jt_autorig_legs_ankle_select_text', q=True, tx=True)
    ball               = cmds.textField('jt_autorig_legs_ball_select_text', q=True, tx=True)
    toes               = cmds.textField('jt_autorig_legs_toes_select_text', q=True, tx=True)
    reverse_foot_root  = cmds.textField('jt_autorig_legs_reverse_foot_root_select_text', q=True, tx=True)
    reverse_foot_heel  = cmds.textField('jt_autorig_legs_reverse_foot_heel_select_text', q=True, tx=True)
    reverse_foot_toes  = cmds.textField('jt_autorig_legs_reverse_foot_toes_select_text', q=True, tx=True)
    reverse_foot_ball  = cmds.textField('jt_autorig_legs_reverse_foot_ball_select_text', q=True, tx=True)
    reverse_foot_ankle = cmds.textField('jt_autorig_legs_reverse_foot_ankle_select_text', q=True, tx=True)
    rig_l    = cmds.checkBox('jt_autorig_leg_rig_L', q=True, value=True)
    rig_r    = cmds.checkBox('jt_autorig_leg_rig_R', q=True, value=True)
    roll     = cmds.optionMenu('jt_autorig_legs_roll_combo', q=True, v=True)
    yaw      = cmds.optionMenu('jt_autorig_legs_yaw_combo', q=True, v=True)
    pitch    = cmds.optionMenu('jt_autorig_legs_pitch_combo', q=True, v=True)

    if rig_l:
        rig_region_name = 'L_leg'
        create_leg_rig(base_curve, rig_region_name, pelvis, hip, knee, ankle, ball, toes, reverse_foot_root, reverse_foot_heel, reverse_foot_toes, reverse_foot_ball, reverse_foot_ankle, roll, yaw, pitch, 'L')
    if rig_r:
        rig_region_name = 'R_leg'
        create_leg_rig(base_curve, rig_region_name, pelvis, hip, knee, ankle, ball, toes, reverse_foot_root, reverse_foot_heel, reverse_foot_toes, reverse_foot_ball, reverse_foot_ankle, roll, yaw, pitch, 'R')


def ui_remove_leg_rig():

    base_curve = cmds.textField('jt_autorig_base_name_select_text', q=True, tx=True)
    hip        = cmds.textField('jt_autorig_legs_hip_select_text', q=True, tx=True)
    rig_l      = cmds.checkBox('jt_autorig_leg_rig_L', q=True, value=True)
    rig_r      = cmds.checkBox('jt_autorig_leg_rig_R', q=True, value=True)

    if rig_l:
        de_rig_element(base_curve, 'L_leg', change_prefix(hip, 'L'))
    if rig_r:
        de_rig_element(base_curve, 'R_leg', change_prefix(hip, 'R'))


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


def create_leg_rig(base_curve, rig_region_name, pelvis, hip, knee, ankle, ball, toes, reverse_foot_root, reverse_foot_heel, reverse_foot_toes, reverse_foot_ball, reverse_foot_ankle, roll, yaw, pitch, side):

    # create group to contain all rigging nodes
    cmds.select(cl=True)
    leg_group = cmds.group(em=True, n=rig_region_name + '_group')
    cmds.select(leg_group, base_curve, r=True)
    cmds.parent()

    # add the leg group node to the base curve rig nodes attr
    add_node_to_rig_nodes(base_curve, rig_region_name, leg_group)

    hip                = change_prefix(hip, side)
    knee               = change_prefix(knee, side)
    ankle              = change_prefix(ankle, side)
    ball               = change_prefix(ball, side)
    toes               = change_prefix(toes, side)
    reverse_foot_root  = change_prefix(reverse_foot_root, side)
    reverse_foot_heel  = change_prefix(reverse_foot_heel, side)
    reverse_foot_toes  = change_prefix(reverse_foot_toes, side)
    reverse_foot_ball  = change_prefix(reverse_foot_ball, side)
    reverse_foot_ankle = change_prefix(reverse_foot_ankle, side)

    # add ik/fk switch handle
    ik_fk_switch_curve, ik_fk_switch_group = jt_ctl_curve.create(hip, 'paddle_3', True)
    cmds.select(ik_fk_switch_curve)
    cmds.rotate(90,0,90, os=True)
    if side == 'R':
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
    ik_ball  = duplicate_joint_without_children(ball, '_ik')
    ik_toes  = duplicate_joint_without_children(toes, '_ik')

    # duplicate joints for fk
    fk_hip   = duplicate_joint_without_children(hip, '_fk')
    fk_knee  = duplicate_joint_without_children(knee, '_fk')
    fk_ankle = duplicate_joint_without_children(ankle, '_fk')
    fk_ball  = duplicate_joint_without_children(ball, '_fk')
    fk_toes  = duplicate_joint_without_children(toes, '_fk')

    # rebuild ik joints
    cmds.select(ik_knee, ik_hip, r=True)
    cmds.parent()
    cmds.select(ik_ankle, ik_knee, r=True)
    cmds.parent()
    cmds.select(ik_ball, ik_ankle, r=True)
    cmds.parent()
    cmds.select(ik_toes, ik_ball, r=True)
    cmds.parent()

    # rebuild fk joints
    cmds.select(fk_knee, fk_hip, r=True)
    cmds.parent()
    cmds.select(fk_ankle, fk_knee, r=True)
    cmds.parent()
    cmds.select(fk_ball, fk_ankle, r=True)
    cmds.parent()
    cmds.select(fk_toes, fk_ball, r=True)
    cmds.parent()

    # parent constrain ik and fk bones to skeleton
    cmds.select(ik_hip, r=True)
    ik_hip_group = cmds.group(n=side + '_ik_leg_bones')
    cmds.select(pelvis, ik_hip_group, r=True)
    cmds.parentConstraint(mo=True, weight=1)
    cmds.scaleConstraint(mo=True, weight=1)
    cmds.connectAttr(ik_fk_switch_curve + '.bone_visibility', ik_hip_group + '.visibility', f=True)

    cmds.select(fk_hip, r=True)
    fk_hip_group = cmds.group(n=side + '_fk_leg_bones')
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
    ball_blend = create_blend(ik_ball + '.rotate', fk_ball + '.rotate', ball + '.rotate', ik_fk_switch_curve + '.ik_fk_blend')

    # connect reverse foot visibility
    cmds.connectAttr(ik_fk_switch_curve + '.bone_visibility', reverse_foot_root + '.visibility', f=True)

    # add blend nodes to base curve rig nodes attr
    add_node_to_rig_nodes(base_curve, rig_region_name, (hip_blend, knee_blend, ankle_blend, ball_blend))

    # create ik foot ctl curve
    foot_curve, foot_curve_group = jt_ctl_curve.create(reverse_foot_heel, 'square', False, lock_unused=False)
    cmds.select(foot_curve)
    cmds.setAttr(foot_curve + '.rotate', 90, 0, 0)
    cmds.setAttr(foot_curve + '.scale', 0.6, 1, 1.2)
    cmds.setAttr(foot_curve + '.translate', 0.2, 11,0)
    cmds.makeIdentity(apply=True, t=1, r=1, s=1, n=0)
    cmds.setAttr(foot_curve + '.rotatePivot', 0,0,0)
    cmds.setAttr(foot_curve + '.scalePivot', 0,0,0)
    if side == 'R':
        cmds.setAttr(foot_curve + '.scale', 1,-1,1)
        cmds.makeIdentity(apply=True, t=0, r=1, s=1, n=0)
    cmds.connectAttr(ik_fk_switch_curve + '.ik_visibility', foot_curve_group + '.visibility', f=True)

    # add reverse foot attrs to foot curve
    for attr in ('foot_break', 'foot_roll', 'heel_pivot', 'toes_pivot', 'heel', 'ball', 'toes'):
        add_keyable_attr(foot_curve, attr, 'float')

    # initialise foot break
    cmds.setAttr(foot_curve + '.foot_break', 20)

    # ofset toe roll
    inverse_foot_break = create_mult(foot_curve + '.foot_break', side + '_inverse_foor_break', -1)
    toe_offset = create_add(foot_curve + '.foot_roll', side + '_toe_offset', inverse_foot_break + '.outputX')

    # create clamp nodes
    heel_clamp = create_clamp(foot_curve + '.foot_roll', side + '_heel_clamp', -360, 0)
    ball_clamp = create_clamp(foot_curve + '.foot_roll', side + '_ball_clamp', 0, foot_curve + '.foot_break')
    toes_clamp  = create_clamp(toe_offset + '.output1D', side + '_toe_clamp' , 0, 360)

    # create sum nodes for foot roll override attrs
    heel_sum = create_add(heel_clamp + '.outputR', side + '_heel_sum', foot_curve + '.heel')
    ball_sum = create_add(ball_clamp + '.outputR', side + '_ball_sum', foot_curve + '.ball')
    toes_sum = create_add(toes_clamp + '.outputR', side + '_toes_sum', foot_curve + '.toes')

    # add foot roll utilities to base curve rig nodes attr
    add_node_to_rig_nodes(base_curve, rig_region_name, (inverse_foot_break, toe_offset, heel_clamp, ball_clamp, toes_clamp, heel_sum, ball_sum, toes_sum))

    # connect up sum nodes and remaninig attrs to bones attrs
    cmds.connectAttr(heel_sum + '.output1D', reverse_foot_heel + '.rotate' + yaw, f=True)
    cmds.connectAttr(ball_sum + '.output1D', reverse_foot_ball + '.rotate' + yaw, f=True)
    cmds.connectAttr(toes_sum + '.output1D', reverse_foot_toes + '.rotate' + yaw, f=True)
    cmds.connectAttr(foot_curve + '.heel_pivot', reverse_foot_heel + '.rotate' + pitch, f=True)
    cmds.connectAttr(foot_curve + '.toes_pivot', reverse_foot_toes + '.rotate' + pitch, f=True)



    # parent ik foot ctl to leg group
    cmds.select(foot_curve_group, leg_group, r=True)
    cmds.parent()

    cmds.select(foot_curve, reverse_foot_root, r=True)
    cmds.parentConstraint(mo=True, weight=1)
    cmds.scaleConstraint(mo=True, weight=1)

    # create ik handles for leg
    cmds.select(ik_hip + '.rotatePivot', ik_ankle + '.rotatePivot', r=True)
    hip_ankle_ik_handle, hip_ankle_ik_effector = cmds.ikHandle(sol='ikRPsolver')
    cmds.connectAttr(ik_fk_switch_curve + '.bone_visibility', hip_ankle_ik_handle + '.visibility', force=True)

    cmds.select(ik_ankle + '.rotatePivot', ik_ball + '.rotatePivot', r=True)
    ankle_ball_ik_handle, ankle_ball_ik_effector = cmds.ikHandle(sol='ikSCsolver')
    cmds.connectAttr(ik_fk_switch_curve + '.bone_visibility', ankle_ball_ik_handle + '.visibility', force=True)

    cmds.select(ik_ball + '.rotatePivot', ik_toes + '.rotatePivot', r=True)
    ball_toes_ik_handle, ball_toes_ik_effector = cmds.ikHandle(sol='ikSCsolver')
    cmds.connectAttr(ik_fk_switch_curve + '.bone_visibility', ball_toes_ik_handle + '.visibility', force=True)

    # parent reverse foot ik handles to leg group
    cmds.select([hip_ankle_ik_handle, ankle_ball_ik_handle, ball_toes_ik_handle], leg_group, r=True)
    cmds.parent()

    # parent ik handles to reverse foot
    cmds.select(reverse_foot_ankle ,hip_ankle_ik_handle, r=True)
    cmds.parentConstraint(mo=True, weight=1)

    cmds.select(reverse_foot_ball ,ankle_ball_ik_handle, r=True)
    cmds.parentConstraint(mo=True, weight=1)

    cmds.select(reverse_foot_toes ,ball_toes_ik_handle, r=True)
    cmds.parentConstraint(mo=True, weight=1)

    # create pole vecotor ctl
    pole_vector_curve, pole_vector_curve_group = jt_ctl_curve.create(ik_knee, 'cube', False, lock_unused=False)
    cmds.select(pole_vector_curve, r=True)
    cmds.setAttr(pole_vector_curve + '.scale', 0.2, 0.2, 0.2)
    cmds.makeIdentity(apply=True, t=0, r=1, s=1, n=0)
    cmds.select(pole_vector_curve, hip_ankle_ik_handle, r=True)
    cmds.poleVectorConstraint(weight=1)
    cmds.connectAttr(ik_fk_switch_curve + '.ik_visibility', pole_vector_curve_group + '.visibility', f=True)

    # parent ik foot ctl to leg group
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

    fk_ball_curve, fk_ball_curve_group = jt_ctl_curve.create(fk_ball, 'semicircle', True, True, True, True)
    cmds.connectAttr(ik_fk_switch_curve + '.fk_visibility', fk_ball_curve_group + '.visibility', f=True)   
    cmds.select(fk_ball_curve, r=True)
    cmds.setAttr(fk_ball_curve + '.scale', 0.5, 0.5, -0.5)
    cmds.makeIdentity(apply=True, t=0, r=1, s=1, n=0)

    # parent fk controlls to leg group
    cmds.select(fk_ankle_curve_group, fk_ball_curve_group, leg_group, r=True)
    cmds.parent()


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

