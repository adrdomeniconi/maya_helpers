import maya.cmds as cmds
import maya.OpenMaya as om

def create_child_group():
    """Creates a child group on the selected node.

    Parameters
    ----------
        no params.
    
    Returns
    -------
        no return. 
    """
    selection = cmds.ls(selection=True)
    new_grp = cmds.group(name="child_grp", empty=True)
    
    if selection:
        parent = selection[0]
        
        grp_pos = cmds.xform(parent, query=True, worldSpace=True, matrix=True)
        cmds.xform(new_grp, worldSpace=True, matrix=grp_pos)
        
        new_grp = cmds.rename(new_grp, "{0}_offset".format(parent))
        
        cmds.parent(new_grp, parent)

def create_group_parent_by_selection():
    """Creates a group parent structure for the selected node.

    Parameters
    ----------
        no parameters.
    
    Returns
    -------
        no return. 
    """
    selection = cmds.ls(selection=True)
    
    if not __is_valid(selection):
        om.MGlobal.displayError("Please select a transform object.")
        return
    
    for node in selection:
        create_group_parent(node)

def create_group_parent(target, custom_structure=[], replace_suffix = False, reparent = False):
    """Creates a group parent structure.

    Parameters
    ----------
    target : str
        Target node where the group structure will be created.
    custom_structure : list
        Creates the structure with custom hierarchy. Ex: ["offset", "driver", "world"]
    replace_suffix : bool, optional
        If set to True the target object suffix will not be added to the created groups. Otherwise, the suffix of the groups will be appended after the original suffix on the groups names.
    
    Returns
    -------
    str
        The most external created group name. 
    """

    if custom_structure:
        return __create_group_parent_custom(target, custom_structure, replace_suffix = replace_suffix, reparent = reparent)
    
    parent = cmds.listRelatives(target, parent=True)

    target_translation = cmds.xform(target, query=True, worldSpace=True, translation=True)
    target_rotation = cmds.xform(target, query=True, worldSpace=True, rotation=True)
    
    offset_group = __create_group(target, target_translation, target_rotation, "offset")
    external_group = __create_group(target, target_translation, target_rotation, "world")
    
    cmds.parent(target, offset_group)
    cmds.parent(offset_group, external_group)

    if reparent and parent is not None:
        cmds.parent(external_group, parent)

    return external_group
        
def __create_group_parent_custom(target, custom_structure, replace_suffix = False, reparent = False):
    
    parent = cmds.listRelatives(target, parent=True)

    target_translation = cmds.xform(target, query=True, worldSpace=True, translation=True)
    target_rotation = cmds.xform(target, query=True, worldSpace=True, rotation=True)

    custom_structure.reverse()
    groups = []

    for item in custom_structure:
        group = __create_group(target, target_translation, target_rotation, item, replace_suffix = replace_suffix)
        groups.append(group)
        if len(groups) > 1:
            cmds.parent(groups[-2], groups[-1])
    
    cmds.parent(target, groups[0])
    
    if reparent and parent is not None:
        cmds.parent(groups[-1], parent)

    return groups[0]

def __is_valid(selection):
    
    is_valid = cmds.nodeType(selection[0]) == 'transform' or cmds.nodeType(selection[0]) == 'ikHandle'
    
    return is_valid
    
def __create_group(name, translation, rotation, suffix, replace_suffix=False):

    if replace_suffix:
        suffix_idx = name.rfind("_")
        name = name[:suffix_idx]

    group_name = "{0}_{1}".format(name, suffix)
    group = cmds.group(name=group_name, empty=True)
    cmds.xform(group, translation=translation)
    cmds.xform(group, rotation=rotation)
    
    return group
        
        
if __name__ == "__main__":
    pass