
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

shapes = {
    'cube'       : [(12.00000000000002, 12.0, 12.0), (-12.0, 12.0, 12.0), (-12.0, 12.0, -12.0), (12.00000000000002, 12.0, -12.0), (12.00000000000002, 12.0, 12.0), (12.00000000000002, -11.999999999999998, 12.0), (-12.0, -11.999999999999998, 12.0), (-12.0, 12.0, 12.0), (-12.0, 12.0, -12.0), (-12.0, -12.000000000000002, -12.000000000000012), (-12.0, -12.000000000000002, 12.000000000000012), (-12.0, -12.000000000000002, -12.000000000000012), (12.00000000000002, -11.999999999999998, -12.000000000000012), (12.00000000000002, 12.0, -12.000000000000014), (12.00000000000002, -11.999999999999998, -12.000000000000012), (12.00000000000002, -12.000000000000002, 12.000000000000012)],
    'paddle'     : [(0.0, 0.0, 0.0), (0.0, 8.0, 0.0), (-2.0, 8.0, 0.0), (-2.0, 12.0, 0.0), (2.0, 12.0, 0.0), (2.0, 8.0, 0.0), (0.0, 8.0, 0.0)],
    'paddle_2'   : [(0.0, 0.0, 0.0), (0.0, 8.0, 0.0), (-2.0, 9.0, 0.0), (-2.0, 11.0, 0.0), (0.0, 12.0, 0.0), (2.0, 11.0, 0.0), (2.0, 9.0, 0.0), (0.0, 8.0, 0.0)],
    'star_5'     : [(2.8478397237640797e-16, 3.2799875133324369e-16, -4.6508752168325955), (-7.0778717074991064, 5.965165559654916e-16, -9.7418546536162047), (-4.4232451814444893, 1.3121786614672325e-16, -1.4371994807186663), (-11.452236990744808, -2.2784904952678884e-16, 3.7210573642200551), (-2.7337158627067613, -1.8718029442132456e-16, 3.7626370891350103), (-7.3733501287740533e-16, -7.3733501287740533e-16, 12.041594578792296), (2.7337158627067613, -1.8718029442132456e-16, 3.7626370891350103), (11.452236990744808, -2.2784904952678894e-16, 3.7210573642200577), (4.4232451814444893, 1.3121786614672325e-16, -1.4371994807186677), (7.0778717074991064, 5.965165559654916e-16, -9.7418546536162047), (2.8478397237640797e-16, 3.2799875133324369e-16, -4.6508752168325955)],
    'star_30'    : [(9.456593898693871e-16, 5.8765160310113578e-16, -9.5970789865335888), (-2.494940289813111, 7.1873119699939107e-16, -11.737771208805668), (-3.8926869357611462, 5.3698697607383733e-16, -8.7696628358104149), (-7.0534230275096776, 5.9445604357025521e-16, -9.7082039324993712), (-7.1122929363785845, 3.9375346927864291e-16, -6.4304821529405762), (-10.392304845413266, 3.6739403974420613e-16, -6.0000000000000027), (-9.1021188751432973, 1.8271745727600519e-16, -2.9840025287816903), (-11.934262744419284, 7.6806268776314308e-17, -1.254341559211845), (-9.5181057702416805, -5.9631016256839926e-17, 0.97384839936473733), (-11.412678195541847, -2.2706200382604892e-16, 3.7082039324993681), (-8.2883257083889141, -2.9138769857929997e-16, 4.7587222500753015), (-8.9177379057287354, -4.9166919317334209e-16, 8.0295672763063006), (-5.6254188344805156, -4.7247975387446054e-16, 7.7161799500626556), (-4.8808397169096081, -6.7126231234656928e-16, 10.962545491711214), (-1.989825938764707, -5.7159472061211359e-16, 9.3348501953392518), (-4.0654571533638829e-15, -7.3478807948841227e-16, 12.000000000000004), (1.9898259387646835, -5.7159472061211378e-16, 9.3348501953392464), (4.8808397169096009, -6.7126231234656948e-16, 10.962545491711218), (5.6254188344805014, -4.7247975387446054e-16, 7.7161799500626556), (8.9177379057287354, -4.9166919317334239e-16, 8.029567276306306), (8.2883257083888857, -2.9138769857930017e-16, 4.7587222500753148), (11.412678195541853, -2.2706200382604946e-16, 3.708203932499377), (9.5181057702416805, -5.9631016256840357e-17, 0.97384839936474676), (11.934262744419293, 7.6806268776313852e-17, -1.2543415592118374), (9.1021188751433169, 1.8271745727600519e-16, -2.9840025287816903), (10.392304845413276, 3.6739403974420604e-16, -6.0000000000000018), (7.1122929363785987, 3.9375346927864291e-16, -6.4304821529405762), (7.0534230275096883, 5.944560435702553e-16, -9.7082039324993747), (3.8926869357611458, 5.3698697607383743e-16, -8.7696628358104078), (2.4949402898131203, 7.1873119699939156e-16, -11.737771208805675), (5.7271017108170161e-15, 5.8765160310113607e-16, -9.5970789865336297)],
    'waist'      : [(-12.0, 0.0, -12.0), (-12.0, 0.0, 12.0), (12.0, 0.0, 12.0), (12.0, 0.0, -12.0), (-12.0, 0.0, -12.0), (0.0, -12.0, 0.0), (12.0, 0.0, -12.0), (12.000000000000012, 0.0, 12.000000000000004), (0.0, -12.0, 0.0), (-12.0, 0.0, 12.000000000000004)],
    'circle'     : [(7.3478807948841188e-16, 7.3478807948841188e-16, -12.0), (-4.5922011883810772, 6.7885566737262011e-16, -11.08655439013544), (-8.4852813742385713, 5.1957363374129592e-16, -8.4852813742385695), (-11.08655439013544, 2.811912243195779e-16, -4.5922011883810772), (-12.0, -3.6585070926957735e-32, 5.9747955006177597e-16), (-11.08655439013544, -2.8119122431957795e-16, 4.592201188381078), (-8.4852813742385695, -5.1957363374129602e-16, 8.4852813742385713), (-4.5922011883810763, -6.788556673726203e-16, 11.086554390135442), (1.2636133648368699e-15, -7.3478807948841188e-16, 12.0), (4.5922011883810789, -6.7885566737262011e-16, 11.08655439013544), (8.4852813742385713, -5.1957363374129582e-16, 8.4852813742385678), (11.086554390135442, -2.8119122431957771e-16, 4.5922011883810745), (12.0, 1.5895186753717793e-31, -2.5958809943870575e-15), (11.08655439013544, 2.8119122431957805e-16, -4.5922011883810798), (8.4852813742385678, 5.1957363374129602e-16, -8.4852813742385713), (4.5922011883810736, 6.7885566737262011e-16, -11.08655439013544), (-3.928148623937245e-15, 7.3478807948841168e-16, -11.999999999999996)],
    'square'     : [(12.0, 0.0, 12.0), (12.0, 0.0, -12.0), (-12.0, 0.0, -12.0), (-12.0, 0.0, 12.0), (12.0, 0.0, 12.0)],
    'diamond'    : [(-12.0, 0.0, 0.0), (0.0, 0.0, 12.0), (12.0, 0.0, 0.0), (0.0, 0.0, -12.0), (-12.0, 0.0, 0.0), (0.0, 12.0, 0.0), (12.0, 0.0, 0.0), (0.0, -12.0, 0.0), (-12.0, 0.0, 0.0), (0.0, 0.0, 12.0), (0.0, 12.000000000000004, 0.0), (0.0, 0.0, -12.000000000000011), (0.0, -12.000000000000004, 0.0), (0.0, 0.0, 12.000000000000011)],
    'paddle_3'   : [(0.0, 0.0, 0.0), (0.0, 1.7763568394002505e-15, 8.0), (-2.0, 1.9984014443252818e-15, 9.0), (-2.0, 2.4424906541753444e-15, 11.0), (0.0, 2.6645352591003757e-15, 12.0), (2.0, 2.4424906541753444e-15, 11.0), (2.0, 1.9984014443252818e-15, 9.0), (0.0, 1.7763568394002505e-15, 8.0)],
    'semicircle' : [(-12.0, -3.6585070926957735e-32, 5.9747955006177597e-16), (-11.08655439013544, -2.8119122431957795e-16, 4.592201188381078), (-8.4852813742385695, -5.1957363374129602e-16, 8.4852813742385713), (-4.5922011883810763, -6.788556673726203e-16, 11.086554390135442), (1.2636133648368699e-15, -7.3478807948841188e-16, 12.0), (4.5922011883810789, -6.7885566737262011e-16, 11.08655439013544), (8.4852813742385713, -5.1957363374129582e-16, 8.4852813742385678), (11.086554390135442, -2.8119122431957771e-16, 4.5922011883810745), (12.0, 1.5895186753717793e-31, -2.5958809943870575e-15)]
}

def load_ui():
    current_script_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    if (cmds.window('jt_ctl_curve', exists=True)):
        cmds.deleteUI('jt_ctl_curve')
    window = cmds.loadUI(uiFile=os.path.join(current_script_path, 'jt_ctl_curve.ui'))

    for key in shapes.keys():
        cmds.textScrollList('jt_ctl_curve_ui_list', e=True, append=key)

    cmds.showWindow(window)

def create(object=None, curve_name='circle', parent_ctl=True, xrot=False, yrot=False, zrot=False, xscale=False, yscale=False, zscale=False, xtrans=False, ytrans=False, ztrans=False, align=True, lock_unused=True):

    if curve_name == None:
        curve_key = 'circle'
    elif curve_name not in shapes:
        curve_key = 'circle'
    else:
        curve_key = curve_name

    # re orient handle
    if object is None:
        cmds.curve(n='ctl_curve', degree=1, p=shapes[curve_key])
    else:
        cmds.curve(n=object + '_ctl', degree=1, p=shapes[curve_key])

    curve_name = cmds.ls(sl=True)[0]
    cmds.group(n=curve_name + '_group')
    cmds.xform(os=True, piv=[0,0,0])

    group_name = cmds.ls(sl=True)[0]

    if object is not None:
        bone_world_space_rotation_axis = cmds.xform(object, ws=True, ro=True, q=True)
        bone_world_space_transform = cmds.xform(object, ws=True, t=True, q=True)

        # align group to bone
        cmds.setAttr(group_name + '.translateX', bone_world_space_transform[0])
        cmds.setAttr(group_name + '.translateY', bone_world_space_transform[1])
        cmds.setAttr(group_name + '.translateZ', bone_world_space_transform[2])
        if align:
            cmds.setAttr(group_name + '.rotateX', bone_world_space_rotation_axis[0])
            cmds.setAttr(group_name + '.rotateY', bone_world_space_rotation_axis[1])
            cmds.setAttr(group_name + '.rotateZ', bone_world_space_rotation_axis[2])

    if parent_ctl == True:     
        # if the initial object has a parent, parent the control group to it
        if cmds.listRelatives(object, ap=True, ad=False) is not None:
            cmds.select(cmds.listRelatives(object, ap=True, ad=False)[0], r=True)
            cmds.select(group_name, add=True)
            
            cmds.parentConstraint(mo=True, weight=1)
            cmds.scaleConstraint(mo=True, weight=1)

            cmds.select(curve_name, r=True)

    if object is not None:
        if xrot:
            cmds.connectAttr((curve_name + '.rotate.rotateX'), (object + '.rotate.rotateX'), force=True)
        if yrot:
            cmds.connectAttr((curve_name + '.rotate.rotateY'), (object + '.rotate.rotateY'), force=True)
        if yrot:
            cmds.connectAttr((curve_name + '.rotate.rotateZ'), (object + '.rotate.rotateZ'), force=True)

        if xscale:
            cmds.connectAttr((curve_name + '.scale.scaleX'), (object + '.scale.scaleX'), force=True)
        if yscale:
            cmds.connectAttr((curve_name + '.scale.scaleY'), (object + '.scale.scaleY'), force=True)
        if yscale:
            cmds.connectAttr((curve_name + '.scale.scaleZ'), (object + '.scale.scaleZ'), force=True)

        if xtrans:
            cmds.connectAttr((curve_name + '.translate.translateX'), (object + '.translate.translateX'), force=True)
        if ytrans:
            cmds.connectAttr((curve_name + '.translate.translateY'), (object + '.translate.translateY'), force=True)
        if ytrans:
            cmds.connectAttr((curve_name + '.translate.translateZ'), (object + '.translate.translateZ'), force=True)

        if lock_unused:
            for item in ('.rotate.rotateX', '.rotate.rotateY', '.rotate.rotateZ', '.scale.scaleX', '.scale.scaleY', '.scale.scaleZ', '.translate.translateX', '.translate.translateY', '.translate.translateZ'):
                cmds.setAttr(curve_name + item, keyable=False, channelBox=False)

            if xrot:
                cmds.setAttr(curve_name + '.rotate.rotateX', channelBox=True)
                cmds.setAttr(curve_name + '.rotate.rotateX', keyable=True)
            if yrot:
                cmds.setAttr(curve_name + '.rotate.rotateY', channelBox=True)
                cmds.setAttr(curve_name + '.rotate.rotateY', keyable=True)
            if yrot:
                cmds.setAttr(curve_name + '.rotate.rotateZ', channelBox=True)
                cmds.setAttr(curve_name + '.rotate.rotateZ', keyable=True)

            if xscale:
                cmds.setAttr(curve_name + '.scale.scaleX', channelBox=True)
                cmds.setAttr(curve_name + '.scale.scaleX', keyable=True)
            if yscale:
                cmds.setAttr(curve_name + '.scale.scaleY', channelBox=True)
                cmds.setAttr(curve_name + '.scale.scaleY', keyable=True)
            if yscale:
                cmds.setAttr(curve_name + '.scale.scaleZ', channelBox=True)
                cmds.setAttr(curve_name + '.scale.scaleZ', keyable=True)

            if xtrans:
                cmds.setAttr(curve_name + '.translate.translateX', channelBox=True)
                cmds.setAttr(curve_name + '.translate.translateX', keyable=True)
            if ytrans:
                cmds.setAttr(curve_name + '.translate.translateY', channelBox=True)
                cmds.setAttr(curve_name + '.translate.translateY', keyable=True)
            if ytrans:
                cmds.setAttr(curve_name + '.translate.translateZ', channelBox=True)
                cmds.setAttr(curve_name + '.translate.translateZ', keyable=True)

    return(curve_name, group_name)


def create_from_ui():
    if cmds.textScrollList('jt_ctl_curve_ui_list', q=True, si=True) is None:
        curve_name = 'circle'
    else:
        curve_name = cmds.textScrollList('jt_ctl_curve_ui_list', q=True, si=True)[0]

    object = cmds.ls(sl=True)
    if object == []:
        object = None
    else:
        object = object[0]

    create(object,
            curve_name,
            cmds.checkBox('jt_ctl_curve_ui_parent_curve', q=True, value=True),
            cmds.checkBox('jt_ctl_curve_ui_rotX', q=True, value=True),
            cmds.checkBox('jt_ctl_curve_ui_rotY', q=True, value=True),
            cmds.checkBox('jt_ctl_curve_ui_rotZ', q=True, value=True),
            cmds.checkBox('jt_ctl_curve_ui_scaleX', q=True, value=True),
            cmds.checkBox('jt_ctl_curve_ui_scaleY', q=True, value=True),
            cmds.checkBox('jt_ctl_curve_ui_scaleZ', q=True, value=True),
            cmds.checkBox('jt_ctl_curve_ui_transformX', q=True, value=True),
            cmds.checkBox('jt_ctl_curve_ui_transformY', q=True, value=True),
            cmds.checkBox('jt_ctl_curve_ui_transformZ', q=True, value=True))

