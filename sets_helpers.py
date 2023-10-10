import maya.cmds as cmds

def move_set(set_name, source_mesh, target_mesh):
    """Move a selection set to another identical mesh. 

    Parameters
    ----------
    set_name: str
        Name of the selection set.
    source_mesh: str
        Name of the original mesh.
    target_mesh: selection
        Name of the target_mesh mesh.

    Returns
    -------
        No return.
    """
    destination_vertices = []

    source_vertices = cmds.sets(set_name, query=True)
    cmds.select(source_vertices, replace=True)
    source_vertices = cmds.ls(selection=True, flatten=True)

    for vertice in source_vertices:
        destination_vertices.append(vertice.replace(source_mesh, target_mesh))

    cmds.select(destination_vertices, replace=True)
    cmds.delete(set_name)
    print(cmds.sets(name=set_name))
    cmds.select(clear=True)
    
if __name__ == "__main__":
    pass

