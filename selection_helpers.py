import maya.cmds as cmds
import maya.api.OpenMaya as om
    
def select_joints_on_hierarchy(full_name = False):
    """Select and gets all the joints in a hierarchy. 

    Parameters
    ----------
    source_node: selection
        A node in the hierarchy.
    full_name: selection
        If set to True it will return the nodes with their full name.

    Returns
    -------
        list:
            List of the matching nodes.
    """
    return select_type_on_hierarchy("joint", full_name)
    
def select_constraints_on_hierarchy(full_name = False):
    """Select and gets all the constraints in a hierarchy. 

    Parameters
    ----------
    source_node: selection
        A node in the hierarchy.
    full_name: selection
        If set to True it will return the nodes with their full name.

    Returns
    -------
        list:
            List of the matching nodes.
    """
    return select_type_on_hierarchy("constraint", full_name)

def select_locators_on_hierarchy(full_name = False):
    """Select and gets all the locators in a hierarchy. 

    Parameters
    ----------
    source_node: selection
        A node in the hierarchy.
    full_name: selection
        If set to True it will return the nodes with their full name.

    Returns
    -------
        list:
            List of the matching nodes.
    """
    return select_transform_based_on_shape_on_hierarchy("locator", full_name)
    
def select_type_on_hierarchy(node_type, full_name = False):
    """Select and gets all the nodes of the input type in a hierarchy. 

    Parameters
    ----------
    source_node: selection
        A node in the hierarchy.
    node_type: str
        Node type description.
    full_name: selection
        If set to True it will return the nodes with their full name.

    Returns
    -------
        list:
            List of the matching nodes.
    """
    selection = cmds.ls(selection=True)
    
    if not selection: 
        om.MGlobal.displayError("Please select one object.")
        return
    
    all_nodes = cmds.listRelatives(selection, allDescendents=True, shapes=False, type=node_type, fullPath=full_name)
    
    if all_nodes:
        cmds.select(all_nodes)
        
    return all_nodes
    
def select_transform_based_on_shape_on_hierarchy(node_type, full_name = False):
    """Select and gets all the nodes with sahpes of the input type in a hierarchy. 

    Parameters
    ----------
    source_node: selection
        A node in the hierarchy.
    node_type: str
        Node type (of the sahpe) description.
    full_name: selection
        If set to True it will return the nodes with their full name.

    Returns
    -------
        list:
            List of the matching nodes.
    """
    selection = cmds.ls(selection=True)
    
    if not selection: 
        om.MGlobal.displayError("Please select one object.")
        return
        
    all_shapes = []
    all_nodes = cmds.listRelatives(selection, allDescendents=True, shapes=False, fullPath=full_name)
    
    for node in all_nodes:
        shape = cmds.listRelatives(node, children=True, shapes=True, fullPath=full_name)
        if shape and cmds.nodeType(shape) == node_type:
            all_shapes.append(node)
    
    if all_shapes:
        cmds.select(all_shapes)
        
    return all_shapes
            
if __name__ == "__main__":
    pass