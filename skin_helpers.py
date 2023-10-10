import maya.cmds as cmds
import maya.api.OpenMaya as om
import os
import attributes_helpers as attr
    
def find_related_skin_cluster(mesh):
    """Find the skin cluster related to the input mesh.

    Known issue
    -----------
    Sometimes for some meshes this function just stop working. When it happens if you restart Maya it goes back to normal.

    Parameters
    ----------
    mesh: str
        Mesh name.

    Returns
    -------
        str:
            Skin cluster name.
    """
    mesh_skin = None
    mesh_shapes = cmds.listRelatives(mesh, children=True, shapes=True, fullPath=True)
    
    if mesh_shapes is not None:
        for shape in mesh_shapes: 
            all_connections = cmds.listConnections(shape)
            skin_cluster = cmds.ls(all_connections, type="skinCluster")
            if skin_cluster:
                mesh_skin = skin_cluster[0]
                break
     
    return mesh_skin    

def export_all_skin_weight_to_file(mesh_grp, file_path=None, id="", suffix="skinWeights", version="00"):
    """Identify all the meshes in a group and export their skin weights to separate files in a new folder.

    Parameters
    ----------
    mesh_grp: str
        Mesh group name.
    file_path: str
        Path informing where to files should be saved.
    id: str, optional
        Identifier used on each file name.
    suffix: str, optional
        Suffix used on each file name.
    version: str, optional
        Version number that will be used to name the folder.

    Returns
    -------
        int:
            The quantity of created files.
    """
    mesh_children = cmds.listRelatives(mesh_grp, allDescendents=True, noIntermediate=True,  type="transform", fullPath=True)
    
    directory = "v{0}".format(version)
    parent_dir = file_path
    path = os.path.join(parent_dir, directory)
    os.mkdir(path)

    files_created = 0
    for mesh in mesh_children:
        
        mesh_without_namespace = __get_name_without_namespace(mesh)
        skin_cluster = find_related_skin_cluster(mesh)

        if skin_cluster is None:
            om.MGlobal.displayWarning('Not export skinning from {}'.format(mesh_without_namespace))
            continue
        
        file_name = "{0}_{1}_{2}.xml".format(mesh_without_namespace, id, suffix)
        
        cmds.deformerWeights(file_name, export=True, deformer=skin_cluster, format="XML", path=path)
        files_created += 1
    
    return files_created

def get_all_influence_joints(skin_cluster):
    """Gives all the joints that influences the given skin cluster.

    Parameters
    ----------
    skin_cluster: str
        Skin cluster name.

    Returns
    -------
        list:
            List of joints.
    """
    influences = cmds.skinCluster(skin_cluster, query=True, influence=True)
    return influences

def set_influence_lock(influence, lock=True):
    """Locks a skin cluster influence.

    Parameters
    ----------
    influence: str
        Name of the influence (joint, usually).
    lock: bool
        If set to True it will lock the influence, if False it will unlock the influence.

    Returns
    -------
        No return.
    """
    cmds.setAttr(attr.name(influence, "liw"), lock)

def set_all_influences_lock(influence_list, lock=True):
    """Set the lock attribute to all skin cluster influences.

    Parameters
    ----------
    influence_list: list
        List of all the influence (joints, usually).
    lock: bool
        If set to True it will lock the influences, if False it will unlock the influences.

    Returns
    -------
        No return.
    """
    for inf in influence_list:
            cmds.setAttr(attr.name(inf, "liw"), lock)

def move_influence_between_jnts(source, target, skin_cluster, vertices):
    """Move the influence from one joint to another.

    Parameters
    ----------
    source: str
        Name of the source influence (joint).
    target: str
        Name of the target influence (joint).
    skin_cluster: str
        Name of the skin cluster.
    vertices: list
        List of the vertice to affected by the change.

    Returns
    -------
        No return.
    """

    all_jnts = get_all_influence_joints(skin_cluster)
    set_all_influences_lock(all_jnts, lock=True)
    set_influence_lock(source, lock=False)
    set_influence_lock(target, lock=False)
    
    cmds.skinPercent(skin_cluster, vertices, transformMoveWeights=[source, target])

def copy_skin_in_hierarchy():
    """Copy the skin cluster and weights from all the meshes in a hierarchy to another mesh with the same hierarchy and names.

    Parameters
    ----------
    source: selection
        Root on the source hierarchy
    target: selection
        Root on the target hierarchy

    Returns
    -------
        No return.
    """
    try:
        source, target = __get_selection()
    except:
        om.MGlobal.displayError("Please select exactly two meshes to copy the skin cluster.")
        return
    
    source_children = cmds.listRelatives(source, allDescendents=True, noIntermediate=True,  type="transform", fullPath=True)
    target_children = cmds.listRelatives(target, allDescendents=True, noIntermediate=True, type="transform", fullPath=True)
    
    for source_mesh in source_children:
        
        source_mesh_without_namespace = __get_name_without_namespace(source_mesh)
        
        target_mesh = None
        for target in target_children:
            
            target_mesh_without_namespace = __get_name_without_namespace(target)
            
            if source_mesh_without_namespace == target_mesh_without_namespace:
                target_mesh = target
                break
        
        if target_mesh is None:
            om.MGlobal.displayWarning('Not found target mesh for {0}'.format(source_mesh))
            continue
        
        source_skin = find_related_skin_cluster(source_mesh)
        if source_skin is None:
            om.MGlobal.displayWarning('Not transferred skinning from {} to {}'.format(source_mesh_without_namespace, target_mesh_without_namespace))
            continue
        
        source_skin_influence_joint = cmds.skinCluster(source_skin, query=True, influence=True)
        
        target_skin = find_related_skin_cluster(target_mesh)
        if(target_skin):
            cmds.delete(target_skin)
        
        target_skin = cmds.skinCluster(source_skin_influence_joint, target_mesh, name="{0}_skinCluster".format(target_mesh_without_namespace), toSelectedBones=True)[0]
        
        cmds.copySkinWeights(sourceSkin=source_skin, destinationSkin=target_skin, surfaceAssociation='closestPoint', influenceAssociation='oneToOne', noMirror=True, smooth=False)

        om.MGlobal.displayInfo('Successfully transferred skinning from {} to {}'.format(source_mesh_without_namespace, target_mesh_without_namespace))

def skin_joints_by_hierarchy_from_selection():
    """Skin a list of meshes to a hierarchy of joints.

    Parameters
    ----------
    meshes: selection
        List of meshes 
    joint: selection
        Root on the joint hierarchy

    Returns
    -------
        No return.
    """
    selection = cmds.ls(orderedSelection=True, flatten=True)
    
    if len(selection) < 2:
        raise Exception("Selection error.")
    
    meshes = selection[:-1]
    joint = selection[-1]
    
    if cmds.nodeType(joint) != "joint":
        raise Exception("The last selected object should be a joint.")    
    
    skin_joints_by_hierarchy(joint, meshes)

def skin_joints_by_hierarchy(joint, meshes):
    """Skin a list of meshes to a hierarchy of joints.

    Parameters
    ----------
    meshes: list
        List of meshes 
    joint: str
        Root on the joint hierarchy

    Returns
    -------
        No return.
    """
    joint_chain = cmds.listRelatives(joint, shapes=False, type='joint', allDescendents=True)
    joint_chain.reverse()
    joint_chain.insert(0, joint)
    
    if len(joint_chain) != len(meshes) :
        raise Exception("The number of joints and meshes do not match.")
    
    for idx, joint in enumerate(joint_chain):
        __skin_joint_to_mesh(joint, meshes[idx])

def copy_skin():
    """Copy the skin cluster and weights from on meshe to another.

    Parameters
    ----------
    source: selection
        Source mesh
    target: selection
        Target mesh

    Returns
    -------
        No return.
    """
    try:
        source, target = __get_selection()
    except:
        om.MGlobal.displayError("Please select exactly two meshes to copy the skin cluster.")
        return

    source_skin = find_related_skin_cluster(source)
    source_skin_influence_joint = cmds.skinCluster(source_skin, query=True, influence=True)
    
    target_skin = find_related_skin_cluster(target)
    if(target_skin):
        cmds.delete(target_skin)
    
    target_skin = cmds.skinCluster(source_skin_influence_joint, target, name="{0}_skinCluster".format(target), toSelectedBones=True)[0]
    
    cmds.copySkinWeights(sourceSkin=source_skin, destinationSkin=target_skin, surfaceAssociation='closestPoint', influenceAssociation='oneToOne', noMirror=True, smooth=False)

    om.MGlobal.displayInfo('Successfully transferred skinning from {} to {}'.format(source, target))

def split_weights_between_joints(source_joint, joints, skin_cluster, selection_sets, mirror_selection_sets=False):
    """Split the skin weights from one joint to other joints.

    Parameters
    ----------
    source_joint: str
        Name of the joins which the weights will be taken.
    joints: list
        List of joints that will receive the weights.
    skin_cluster: str
        Skin cluster name.
    selection_sets: list
        Names of the selection sets that will be used to identify thevertices related to each joint.
    mirror_selection_sets = bool, optional
        If set to True, the vertices on the selection set will be mirrored. Useful to avoid creating sets for both sides of a rig.

    Returns
    -------
        No return.
    """
    for jnt, set in zip(joints, selection_sets):
        if jnt == source_joint:
            continue

        vertices = cmds.sets(set, query=True)
        if mirror_selection_sets:
            cmds.symmetricModelling(symmetry=True)
            cmds.select(vertices, replace=True, symmetry=True)
            cmds.select(vertices, deselect=True)
            cmds.symmetricModelling(symmetry=False)
            vertices = cmds.ls(selection=True, flatten=True)
        
        print("Moving weights: {0} to {1}...".format(source_joint, jnt))
        move_influence_between_jnts(source_joint, jnt, skin_cluster, vertices)

def merge_weights_between_joints(target_jnt, joints, skin_cluster):
    """Merge the skin weights from multiple joints to one joint.

    Parameters
    ----------
    target_jnt: str
        Name of the joint that will receive the weights.
    joints: list
        List of joints which the weights will be taken from.
    skin_cluster: str
        Skin cluster name.

    Returns
    -------
        No return.
    """
    for jnt in joints:
        if jnt == target_jnt:
            continue
        
        cmds.select(clear=True)
        cmds.skinCluster(skin_cluster, edit=True, selectInfluenceVerts=jnt)
        vertices = cmds.ls(selection=True)

        print("Moving weights: {0} to {1}...".format(jnt, target_jnt))
        move_influence_between_jnts(jnt, target_jnt, skin_cluster, vertices)
    cmds.select(clear=True)

def __get_name_without_namespace(name):
    
    clean_name = name
    
    if clean_name.find(":") != -1:
        clean_name = name.split(":")[-1]
    
    if clean_name.find("|") != -1:
        clean_name = name.split("|")[-1]
    
    return clean_name
    
def __skin_joint_to_mesh(joint, mesh):
    
    child_meshes = cmds.listRelatives(mesh, shapes=False, children=True, type='transform', fullPath=True)
    
    if not child_meshes:
        print("Skinning {0} to {1}.".format(joint, mesh.split("|")[-1]))
        cmds.skinCluster(joint, mesh, name="{0}_skinCluster".format(mesh.split("|")[-1]), toSelectedBones=True)
    else:
        for child_mesh in child_meshes:
            __skin_joint_to_mesh(joint, child_mesh)

def __get_selection():
    selection = cmds.ls(orderedSelection=True, flatten=True, absoluteName=True)
    
    if len(selection) != 2:
        raise Exception("Selection error.")
        
    source = selection[0]
    target = selection[1]
    
    return source, target

if __name__ == "__main__":
    merge_weights_between_joints("joint1", ["joint2", "joint3", "joint4", "joint5", "joint6"], "skinCluster1")
