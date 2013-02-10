import maya.cmds as cmds
import os
import inspect

def load_ui():

    current_script_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    if (cmds.window('jt_pass_through_bs', exists=True)):
        cmds.deleteUI('jt_pass_through_bs')
    window = cmds.loadUI(uiFile=os.path.join(current_script_path, 'jt_pass_through_bs.ui'))
    cmds.showWindow(window)


def create(mesh, in_out='in', blend_shape_node=None):
    
    cmds.select(mesh, r=True)
    duplicate_object = cmds.duplicate(n=mesh + '_' + in_out + '_bs')[0]

    if in_out == 'in':
        shape_order = [duplicate_object, mesh]
    else:
        shape_order = [mesh, duplicate_object]
        
    if (blend_shape_node is None) or (in_out == 'out'):
        cmds.select(shape_order[0], shape_order[1], r=True)
        blend_shape_node = cmds.blendShape(n=shape_order[0] + '_passthrough', w=[0,1])[0]
        
    else:
        blend_shape_index = len(cmds.getAttr(blend_shape_node + '.weight')[0]) + 2
        cmds.select(shape_order[0], shape_order[1], r=True)
        name = '{0}_passthrough_{1}'.format(shape_order[0], blend_shape_index)
        cmds.blendShape(blend_shape_node, e=True, t=[shape_order[1], blend_shape_index, shape_order[0], 1])
        cmds.setAttr(blend_shape_node + '.' + shape_order[0], 1)

    
    cmds.select(duplicate_object, r=True)
    
    return blend_shape_node


def ui_create_in():

    blend_shape_node = cmds.textField('jt_pass_through_bs_node_name_text', q=True, tx=True)
    selected_objects = cmds.ls(sl=True)
    if selected_objects == []:
        cmds.error('no selection')
        return
    selected_object = selected_objects[0]

    if blend_shape_node == '':
        create(selected_object, 'in')
    else:
        create(selected_object, 'in', blend_shape_node)


def ui_create_out():

    blend_shape_node = cmds.textField('jt_pass_through_bs_node_name_text', q=True, tx=True)
    selected_objects = cmds.ls(sl=True)
    if selected_objects == []:
        cmds.error('no selection')
        return
    selected_object = selected_objects[0]

    if blend_shape_node == '':
        create(selected_object, 'out')
    else:
        create(selected_object, 'out', blend_shape_node)
    

def ui_auto_select():
    
selection = cmds.ls(sl=True)
if selection:
    shapes = cmds.listRelatives(selection[0], s=True)
    print shapes
    for shape in shapes:
        connections = cmds.listConnections(shape, t='blendShape', s=True, d=False)
        if connections:
            cmds.textField('jt_pass_through_bs_node_name_text', e=True, tx=connections[0])




