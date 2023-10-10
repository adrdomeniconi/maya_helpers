import maya.cmds as cmds
import maya.api.OpenMaya as om

def offset_parent_matrix_parent_with_offset():
    """Constrain two objects using offset parent matrix keeping the current position of the driven object. 

    Parameters
    ----------
    driver_object: selection
        A transform object
    driven_object: selection
        A transform object
    
    Returns
    -------
        No return.
    """
    if not __valid_parent_selection():
        om.MGlobal.displayWarning("Select first the parent node and then the child.")
        return 
    
    nodes = cmds.ls(selection=True)
    parent = nodes[0]
    child = nodes[1] 
    
    __opm_parent_with_offset(parent, child)

def transformations_to_offset_parent_matrix(node):
    """Move the transformations values to the offset parent matrix. 

    Parameters
    ----------
    node: str
        A transform node
    
    Returns
    -------
        No return.
    """
    __cp_transformations_to_offset_parent_matrix(node)
    __zero_out_transformations(node)

def transformations_to_offset_parent_matrix_by_selection(hierarchy = False):
    """Move the transformations values to the offset parent matrix. 

    Parameters
    ----------
    node: selection
        A transform node
    hierarchy: bool, optional
        Apply this method to all the object hierarchy.
    
    Returns
    -------
        No return.
    """
    if not __valid_selection():
        om.MGlobal.displayWarning("Select at least one node.")
        return
    
    nodes = __get_nodes(hierarchy)
    
    for node in nodes:
        __cp_transformations_to_offset_parent_matrix(node)
        __zero_out_transformations(node)

def offset_parent_matrix_to_transformations(hierarchy = False):
    """Move the offset parent matrix values to the transformations. 

    Parameters
    ----------
    node: selection
        A transform node
    hierarchy: bool, optional
        Apply this method to all the object hierarchy.
    
    Returns
    -------
        No return.
    """
    if not __valid_selection():
        om.MGlobal.displayWarning("Select at least one node.")
        return
    
    nodes = __get_nodes(hierarchy)
    
    for node in nodes:
        __cp_offset_parent_matrix_to_transformations(node)
        __zero_out_offset_parent_matrix(node)

def zero_out_all(hierarchy = False):
    """Zero out the transformations and offset parent matrix values. 

    Parameters
    ----------
    node: selection
        A transform node
    hierarchy: bool, optional
        Apply this method to all the object hierarchy.
    
    Returns
    -------
        No return.
    """
    if not __valid_selection():
        om.MGlobal.displayWarning("Select at least one node.")
        return
    
    nodes = __get_nodes(hierarchy)
    
    for node in nodes:
        __zero_out_offset_parent_matrix(node)
        __zero_out_transformations(node)
        
def zero_out_opm(hierarchy = False):
    """Zero out the offset parent matrix values. 

    Parameters
    ----------
    node: selection
        A transform node
    hierarchy: bool, optional
        Apply this method to all the object hierarchy.
    
    Returns
    -------
        No return.
    """
    if not __valid_selection():
        om.MGlobal.displayWarning("Select at least one node.")
        return
    
    nodes = __get_nodes(hierarchy)
    
    for node in nodes:
        __zero_out_offset_parent_matrix(node)

def zero_out_opm_keeping_position(hierarchy = False):
    """Zero out the offset parent matrix values but keeping the transform on the same position. 

    Parameters
    ----------
    node: selection
        A transform node
    hierarchy: bool, optional
        Apply this method to all the object hierarchy.
    
    Returns
    -------
        No return.
    """
    if not __valid_selection():
        om.MGlobal.displayWarning("Select at least one node.")
        return 
    
    nodes = __get_nodes(hierarchy)
    
    for node in nodes:
        __zero_out_opm_keeping_position(node)
    
def offset_parent_matrix_parent():
    """Constrain two objects using offset parent matrix. 

    Parameters
    ----------
    driver_object: selection
        A transform object
    driven_object: selection
        A transform object
    
    Returns
    -------
        No return.
    """
    if not __valid_parent_selection():
        om.MGlobal.displayWarning("Select first the parent node and then the child.")
        return 
    
    nodes = cmds.ls(selection=True)
    parent = nodes[0]
    child = nodes[1]
    
    __opm_parent(parent, child)
    __zero_out_transformations(child)

def __zero_out_transformations(node):

    cmds.setAttr("{0}.translateX".format(node), 0)
    cmds.setAttr("{0}.translateY".format(node), 0)
    cmds.setAttr("{0}.translateZ".format(node), 0)
    cmds.setAttr("{0}.rotateX".format(node), 0)
    cmds.setAttr("{0}.rotateY".format(node), 0)
    cmds.setAttr("{0}.rotateZ".format(node), 0)
    
    if cmds.nodeType(node) == "joint":
        cmds.setAttr("{0}.jointOrientX".format(node), 0)
        cmds.setAttr("{0}.jointOrientY".format(node), 0)
        cmds.setAttr("{0}.jointOrientZ".format(node), 0)

def __cp_transformations_to_offset_parent_matrix(node):
    
    source = "{0}.xformMatrix".format(node)
    target = "{0}.offsetParentMatrix".format(node)
    
    cmds.connectAttr(source, target, force=True)
    cmds.disconnectAttr(source, target)

def __cp_offset_parent_matrix_to_transformations(node):
    
    decompose_matrix_node = cmds.createNode("decomposeMatrix", name="temporaryDecomposeMatrix", skipSelect=True)
    
    source_opm = "{0}.offsetParentMatrix".format(node)
    target_decompose_matrix = "{0}.inputMatrix".format(decompose_matrix_node)
    
    source_opm_translations = "{0}.outputTranslate".format(decompose_matrix_node)
    target_node_translations = "{0}.translate".format(node)
    
    source_opm_rotations = "{0}.outputRotate".format(decompose_matrix_node)
    target_node_rotations = "{0}.rotate".format(node)
    
    source_opm_scale = "{0}.outputScale".format(decompose_matrix_node)
    target_node_scale = "{0}.scale".format(node)
    
    cmds.connectAttr(source_opm, target_decompose_matrix, force=True)
    cmds.connectAttr(source_opm_translations, target_node_translations, force=True)
    cmds.connectAttr(source_opm_rotations, target_node_rotations, force=True)
    cmds.connectAttr(source_opm_scale, target_node_scale, force=True)
    
    cmds.disconnectAttr(source_opm, target_decompose_matrix)
    cmds.delete(decompose_matrix_node)
    

def __zero_out_offset_parent_matrix(node):

    identity_matrix = [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]
    cmds.setAttr("{0}.offsetParentMatrix".format(node), *identity_matrix, type="matrix")

def __get_nodes_by_hierarchy():
    
    all_nodes = []
    
    all_descendents = cmds.ls(cmds.listRelatives(allDescendents=True, type="transform"))
    selected = cmds.ls(selection=True)
    
    all_nodes.extend(all_descendents)
    all_nodes.extend(selected)
    
    return all_nodes

def __valid_selection():
    return len(cmds.ls(selection=True)) > 0

def __valid_parent_selection():
    return len(cmds.ls(selection=True)) == 2

def __get_nodes(hierarchy):
    nodes = None
    
    if hierarchy:
        nodes = __get_nodes_by_hierarchy()
    else:
        nodes = cmds.ls(selection=True)
        
    return nodes
    
def __zero_out_opm_keeping_position(node):
    
    node_local_matrix = om.MMatrix(cmds.xform(node, query=True, objectSpace=True, matrix=True))
    node_opm = om.MMatrix(cmds.getAttr("{0}.offsetParentMatrix".format(node)))
    
    node_new_trasnsformation = node_local_matrix * node_opm
    
    cmds.xform(node, matrix=node_new_trasnsformation)
    
    __zero_out_offset_parent_matrix(node)
    
def __opm_parent(parent, child):
    parent_world_matrix = "{0}.worldMatrix".format(parent)
    child_opm = "{0}.offsetParentMatrix".format(child)
    
    cmds.connectAttr(parent_world_matrix, child_opm, force=True)
    
def __opm_parent_with_offset(parent, child):
        
    __zero_out_opm_keeping_position(child)
    
    parent_inverse_world_hold = cmds.createNode("holdMatrix", name="{0}_{1}_opmParentHold".format(parent, child), skipSelect=True)
    cmds.connectAttr("{0}.worldInverseMatrix".format(parent), "{0}.inMatrix".format(parent_inverse_world_hold), force=True)
    cmds.disconnectAttr("{0}.worldInverseMatrix".format(parent), "{0}.inMatrix".format(parent_inverse_world_hold))
    
    parent_offset_multi = cmds.createNode("multMatrix", name="{0}_{1}_opmParentMult".format(parent, child), skipSelect=True)
    cmds.connectAttr("{0}.outMatrix".format(parent_inverse_world_hold), "{0}.matrixIn[0]".format(parent_offset_multi), force=True)
    cmds.connectAttr("{0}.worldMatrix".format(parent), "{0}.matrixIn[1]".format(parent_offset_multi), force=True)
    
    cmds.connectAttr("{0}.matrixSum".format(parent_offset_multi), "{0}.offsetParentMatrix".format(child), force=True)

if __name__ == "__main__":
    offset_parent_matrix_parent_with_offset()
