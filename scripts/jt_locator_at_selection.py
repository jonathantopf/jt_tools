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