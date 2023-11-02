import maya.cmds as cmds
import maya.mel as mel

def create_motion_path(curve_path, driven_object, name="motionPath1", percent_position=0):
    motion_path_node = cmds.createNode("motionPath", name=name)

    cmds.connectAttr(f"{curve_path}.worldSpace", f"{motion_path_node}.geometryPath")
    cmds.connectAttr(f"{motion_path_node}.allCoordinates", f"{driven_object}.translate")
    cmds.setAttr(f"{motion_path_node}.fractionMode", True)
    cmds.setAttr(f"{motion_path_node}.uValue", percent_position)
    cmds.setAttr(f"{motion_path_node}.follow", False)
    
    return motion_path_node

def set_motion_path_position(motion_path_node, percent_position):
    cmds.setAttr(f"{motion_path_node}.uValue", percent_position)