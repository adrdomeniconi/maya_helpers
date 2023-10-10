import maya.cmds as cmds

def rename_in_identical_hierarchy(text_to_replace, new_text):
    """Rename an entire hierarchy based on a the names of a different hierarchy. 

    Parameters
    ----------
    source_node: selection
        The node in the hierarchy that will provide the template for the new name
    target_node: selection
        The node in the hierarchy that will be renamed.

    Returns
    -------
        No return.
    """
    selection = cmds.ls(selection=True)

    source_root = selection[0]
    target_root = selection[1]

    source_nodes = cmds.listRelatives(source_root, allDescendents=True)
    source_nodes.append(source_root)

    target_nodes = cmds.listRelatives(target_root, allDescendents=True)
    target_nodes.append(target_root)

    for idx, source_item in enumerate(source_nodes):
        new_name = source_item.replace(text_to_replace, new_text)
        cmds.rename(target_nodes[idx], new_name)

def rename_numerically_in_hierarchy_by_selection(prefix, suffix):
    """Rename a hierarchy with index numbers. 

    Parameters
    ----------
    root_node: selection
        The node in the hierarchy that will be renamed.
    prefix: str
        Prefix of the new name.
    suffix: str
        Suffix of the new name.

    Returns
    -------
        No return.
    """
    selection = cmds.ls(selection=True)
    root_node = selection[0]

    rename_numerically_in_hierarchy(root_node, prefix, suffix)

def rename_numerically_in_hierarchy(root_node, prefix, suffix):
    """Rename a hierarchy with index numbers. 

    Parameters
    ----------
    root_node: str
        The node in the hierarchy that will be renamed.
    prefix: str
        Prefix of the new name.
    suffix: str
        Suffix of the new name.

    Returns
    -------
        No return.
    """
    source_nodes = cmds.listRelatives(root_node, allDescendents=True, shapes=False, fullPath=True)
    source_nodes.append(root_node)
    new_names = []
    
    for idx, node in enumerate(source_nodes):
        if cmds.nodeType(node) not in ["transform", "joint"]:
            continue
        new_name = "{0}_{1}_{2}".format(prefix, len(source_nodes)-idx-1, suffix)
        new_names.append(cmds.rename(node, new_name))

    return new_names
          
if __name__ == "__main__":
    rename_in_identical_hierarchy("mustache2", "mustache3")