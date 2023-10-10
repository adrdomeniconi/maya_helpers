import maya.cmds as cmds

def set_pivot_to_world_root_by_hierarchy():
    """Move all the transforms pivot to the world root.

    Parameters
    ----------
    transforms : selection
        A transform in hierarchy.
    
    Returns
    -------
        no return.
    """
    children = cmds.listRelatives(allDescendents=True, shapes=False)
    __set_pivot_to_world_root(children)
    
def set_pivot_to_world_root_by_selection():
    """Move all the transforms pivot to the world root.

    Parameters
    ----------
    transforms : selection
        One or more transforms.
    
    Returns
    -------
        no return.
    """
    selection = cmds.ls(selection=True)
    __set_pivot_to_world_root(selection)

def clean_pivots():
    """Zero-out the pivots of the selected meshes.

    Parameters
    ----------
    meshes : selection
        One or more meshes.
    
    Returns
    -------
        no return.
    """
    selection_list = cmds.ls(selection=True)
    
    if not selection_list:
        raise "Select something!"

    for selection in selection_list:
        
        rotate_pivot_attr = "{0}.rotatePivot".format(selection)
        scale_pivot_attr = "{0}.scalePivot".format(selection)
    
    cmds.setAttr(rotate_pivot_attr, 0, 0, 0, type="double3")
    cmds.setAttr(scale_pivot_attr, 0, 0, 0, type="double3")

def unfreeze():
    """Move back the pivots information to the transform attributes.

    Parameters
    ----------
    transforms : selection
        One or more transforms.
    
    Returns
    -------
        no return.
    """
    selection_list = cmds.ls(selection=True)
    
    if not selection_list:
        raise "Select something!"

    for selection in selection_list:
        cmds.makeIdentity(apply=True, translate=True)
        pivots = cmds.xform(selection, query=True, worldSpace=True, pivots=True )
        cmds.xform(selection, objectSpace=True, translation=[pivots[0]*-1, pivots[1]*-1, pivots[2]*-1])
        cmds.makeIdentity(apply=True, translate=True)
        cmds.xform(selection, objectSpace=True, translation=[pivots[0], pivots[1], pivots[2]])

def copy_vtx_pos_from_different_mesh(source_namespace, copy_symmetry=False):
    """Copy the geometry of one mesh to another one if they have the same topology.

    Parameters
    ----------
    vertices: selection
        All the vertices to be copied.
    source_namespace: str
        Namespace of the source mesh (where the vertices will be copied from).
    copy_symmetry: Bool, optional
        If set to True, it will copy and mirror the vertices on the target mesh.
    
    Returns
    -------
        no return.
    """
    selected_vtx = cmds.ls(selection=True, flatten=True)
    symmetry = []
    for vtx in selected_vtx:
        source_pos = cmds.xform(vtx, query=True, worldSpace=True, translation=True)
        source_name_without_namespace = vtx.split(":")[1]
        target_name = "{0}{1}".format(source_namespace, source_name_without_namespace)
        if copy_symmetry:
            cmds.symmetricModelling(symmetry=True)
            cmds.select(target_name, replace=True, symmetry=True)
            cmds.select(target_name, deselect=True)
            cmds.symmetricModelling(symmetry=False)
            symmetric_target_name = cmds.ls(selection=True, flatten=True)
            if symmetric_target_name:
                symmetry.append(symmetric_target_name[0])
                cmds.xform(symmetric_target_name[0], worldSpace=True, translation=[-source_pos[0], source_pos[1], source_pos[2]])
        cmds.xform(target_name, worldSpace=True, translation=source_pos)
    
def symmetrize_vtx(source, target):
    """Moves the target transform/vertice to a mirrored position in relation to the source transform/vertice.  

    Parameters
    ----------
    source: selection
        A selected transform or vertice.
    target: selection
        A selected transform or vertice.
    
    Returns
    -------
        no return.
    """
    source_pos = cmds.xform(source, query=True, worldSpace=True, translation=True)
    cmds.xform(target, worldSpace=True, translation=[-source_pos[0], source_pos[1], source_pos[2]])

def find_not_mirrored_vertices():
    """Identify and selects all the vertices with symmetry problem. Only work if the mesh is in scene root. 

    Parameters
    ----------
    vertices: selection
        One or more vertices.
    
    Returns
    -------
        list:
            A list of vertices with symmetry problem.
    """
    vertices = cmds.ls(selection=True, flatten=True)
    not_mirrored_vertices = []

    for vtx in vertices:
        source_pos = cmds.xform(vtx, query=True, worldSpace=True, translation=True)
        cmds.select(clear=True)
        cmds.symmetricModelling(symmetry=True)
        cmds.select(vtx, replace=True, symmetry=True)
        if len(cmds.ls(selection=True, flatten=True)) != 2:
            not_mirrored_vertices.append(vtx)
        else:
            cmds.select(vtx, deselect=True)
            target_vtx = cmds.ls(selection=True, flatten=True)
            
            if target_vtx:
                target_pos = cmds.xform(target_vtx, query=True, worldSpace=True, translation=True)
            
                if source_pos[0] != -target_pos[0] or source_pos[1] != target_pos[1] or source_pos[2] != target_pos[2]:
                    not_mirrored_vertices.append(vtx)
        
        cmds.symmetricModelling(symmetry=False)

    print(not_mirrored_vertices)
    cmds.select(not_mirrored_vertices, replace=True)

    return not_mirrored_vertices

def __set_pivot_to_world_root(nodes):

    for node in nodes:
        child_nodes = cmds.listRelatives(node, children=True, shapes=True)
        
        if not child_nodes and cmds.nodeType(node) == "transform":
            # print("Group: {0}".format(node), cmds.nodeType(node))
            
            cmds.select(node)
            cmds.makeIdentity(apply=True, normal=False)
            rotate_pivot_attr = "{0}.rotatePivot".format(node)
            scale_pivot_attr = "{0}.scalePivot".format(node)
    
            cmds.setAttr(rotate_pivot_attr, 0, 0, 0, type="double3")
            cmds.setAttr(scale_pivot_attr, 0, 0, 0, type="double3")
            
        elif cmds.nodeType(node) != "mesh":
            # print("Geometry: {0}".format(node), cmds.nodeType(node))
            
            cmds.select(node)
            cmds.move(0,0,0, preserveGeometryPosition=True, scalePivotRelative=True, absolute=True )
            cmds.makeIdentity(apply=True, normal=False)

if __name__ == "__main__":
    clean_pivots()