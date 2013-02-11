
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
import pickle

def load_ui():

    current_script_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    if (cmds.window('jt_copy_skin', exists=True)):
        cmds.deleteUI('jt_copy_skin')
    window = cmds.loadUI(uiFile=os.path.join(current_script_path, 'jt_copy_skin.ui'))
    cmds.showWindow(window)


def copy():

    skin_cluster = None
    mesh_name = None
    selection = cmds.ls(sl=True)
    if selection:
        mesh_name = selection[0]
        shape = cmds.listRelatives(selection[0])
        skin_clusters = cmds.listConnections(shape[0], type='skinCluster')
        if skin_clusters:
            skin_cluster = skin_clusters[0]
        else:
            cmds.error('No skin cluster present')
    else:
        cmds.error('No valid selection')

    bones = cmds.skinCluster(skin_cluster, q=True, inf=True)
    num_verts = cmds.polyEvaluate(mesh_name, v=True)
    data = dict()

    for bone in bones:
        data[bone] = []
        for id in range(num_verts):

            data[bone].append(cmds.skinPercent(skin_cluster, '{0}.vtx[{1}]'.format(mesh_name, id), q=True, t=bone))

    pickled_list = pickle.dumps(data)
    cmds.scrollField('jt_copy_skin_values_field', e=True, tx=pickled_list)
    cmds.skinCluster(mesh_name, e=True, ub=True)


def apply():

    selection = cmds.ls(sl=True)
    if selection:
        mesh_name = selection[0]
    else:
        cmds.error('No mesh selected')

    num_verts = cmds.polyEvaluate(mesh_name, v=True)

    pickled_list = str(cmds.scrollField('jt_copy_skin_values_field', q=True, tx=True))
    data = pickle.loads(pickled_list)

    skin_cluster = cmds.skinCluster(data.keys(), mesh_name, mi=3)[0]

    # shorten the vertex ids is the number of verts has chnaged
    for bone in data.keys():
        if num_verts > len(data[bone]): num_verts = len(data[bone])
        break

    for bone in data.keys():
        for id in range(num_verts):
            cmds.skinPercent(skin_cluster, '{0}.vtx[{1}]'.format(mesh_name, id), tv=[(bone, data[bone][id])], nrm=False)


