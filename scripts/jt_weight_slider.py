import maya.cmds as cmds
import os
import inspect


def load_ui():

    current_script_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    if (cmds.window('jt_weight_slider', exists=True)):
        cmds.deleteUI('jt_weight_slider')
    window = cmds.loadUI(uiFile=os.path.join(current_script_path, 'jt_weight_slider.ui'))
    cmds.showWindow(window)


def get_skinCluster(joints):

    if len(joints) is not 0:
        skin_clusters = cmds.listConnections(joints[0], t='skinCluster')
        if len(skin_clusters) is not 0:
            return skin_clusters[0]

    print('No valid skinclusters found')
    raise Exception


def set_weights():

    slider_value = cmds.intSlider('jt_weight_slider_slider', query=True, v=True) / 100.0
    selected_joints = cmds.ls(sl=True, typ='joint')
    selected_verts = cmds.filterExpand(sm=31)

    if len(selected_joints) == 0:
        cmds.warning('No joints selected')
    
    else:
        skincluster = get_skinCluster(selected_joints)
        cmds.skinPercent(skincluster, tv=(selected_joints[0], slider_value))


def modify_weights(num):

    selected_joints = cmds.ls(sl=True, typ='joint')
    selected_verts = cmds.filterExpand(sm=31)

    if len(selected_joints) == 0:
        cmds.warning('No joints selected')
    
    else:
        skincluster = get_skinCluster(selected_joints)
        cmds.skinPercent(skincluster, tv=(selected_joints[0], num), r=True)











