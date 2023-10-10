import maya.cmds as cmds

def get_parent(node):
    """Gets the parent node

    Parameters
    ----------
    node : str
        Target node
    
    Returns
    -------
    str
        Parent name. 
    """
    return cmds.listRelatives(node, parent=True)[0]

def get_top_parent(node):
    """Gets the top most (most external) parent node.

    Parameters
    ----------
    node : str
        Target node
    
    Returns
    -------
    str
        Top most parent name. 
    """
    current_parent = node
    parent = node
    while current_parent != None:
        current_parent = cmds.listRelatives(current_parent, fullPath=True, parent=True)
        if current_parent is not None:
            current_parent = current_parent[0]
            parent = current_parent
    
    return parent