import os
import maya.cmds as cmds
import maya.mel as mel
import maya.api.OpenMaya as om
import skin_helpers as skin
import attributes_helpers as attr

def generate_delta(original_mesh = "", corrective_mesh = "", destination_path = "", from_selection = False, negate_blendshapes = False, suffix="dlt"):
    """Generates the delta shape between two meshes negating the skin cluster and optionally any other corrective already applied. Can be used selecting both meshes, or informing the meshes on the parameters.

    Parameters
    ----------
    original_mesh : str/selection, optional
        The mesh which the corrective will be applied.
    corrective_mesh : str/selection, optional
        The mesh with the corrections.
    destination_path: str, optional
        The local path where a file with the delta mesh should be saved to.
    from_selection: bool, optional
        If this flag is set to True the "original_mesh" and "corrective_mesh" parameters will be ignored and used the selected meshes instead.
    negate_blendshapes: bool, optional
        If the corrected pose is already influenced by another corrective this flag should be set to True. The generated mesh will negate any corrective already applied to the original mesh and not just the skin cluster.
    suffix: str, optional
        Suffix applied to the name of the delta mesh.

    Returns
    -------
        the name of the generated mesh. 
    """
    if not from_selection:
        cmds.select([original_mesh, corrective_mesh])
    else:
        original_mesh = cmds.ls(selection=True)[0]
        corrective_mesh = cmds.ls(selection=True)[1]

    if negate_blendshapes:
        delta = __invert_shape_with_blendshapes(cancel_blendshapes = True)
    else:
        delta = cmds.invertShape()

    delta_name = "{0}_{1}".format(corrective_mesh, suffix)
    delta_name = cmds.rename(delta, delta_name)
    
    if destination_path:
        file_name = "{0}.ma".format(delta_name)
        full_name = os.path.join(destination_path, file_name)
        cmds.select(clear=True)
        cmds.select(delta_name, replace=True)
        cmds.file(full_name, force=True, options="v=0", typ="mayaAscii", exportSelected=True)
    
    return delta_name

def update_corrective_after_model_updating(old_model_path, old_model_file, old_model_mesh_name, new_model_path, new_model_file, new_model_mesh_name, corrective_path, corrective_file, corrective_mesh_name, new_file_suffix = "updated"):
    """Generates an updated new mesh for a corrective when the original model has been modified.

    Parameters
    ----------
    old_model_path : str
        Local drive path of the model version (not the corrective) before the changes.
    old_model_file : str
        Maya file name of the model version (not the corrective) before the changes.
    old_model_mesh_name: str
        Node name of the mesh on the model version (not the corrective) in the informed Maya file.
    new_model_path : str
        Local drive path of the new model version (not the corrective) after the changes.
    new_model_file : str
        Maya file name of the new model version (not the corrective) after the changes.
    new_model_mesh_name: str
        Node name of the mesh on the new model version (not the corrective) in the informed Maya file.
    corrective_path: str
        Local drive path of corrective.
    corrective_file: str
        Maya file name of the corrective.
    corrective_mesh_name: str
        Node name of the mesh on the corrective Maya file.
    new_file_suffix: str, optional
        Suffix to be added to the new file name after the update.

    Returns
    -------
        No return. 
    """

    cmds.file(new=True, force=True)

    try:
        old_model_namespace = __get_model_from_file(old_model_path, old_model_file)[0]
        new_model_namespace = __get_model_from_file(new_model_path, new_model_file)[0]
        corrective_model_namespace = __get_model_from_file(corrective_path, corrective_file)[0]
    except:
        om.MGlobal.displayError("Update corrective model not completed.")

    old_model = "{0}:{1}".format(old_model_namespace, old_model_mesh_name)
    new_model = "{0}:{1}".format(new_model_namespace, new_model_mesh_name)
    corrective_model = "{0}:{1}".format(corrective_model_namespace, corrective_mesh_name)
    
    blendshape = cmds.blendShape(new_model, corrective_model, old_model, frontOfChain=True, suppressDialog=True)[0]
    cmds.blendShape(blendshape, edit=True, w=[(0, 1), (1, 1)])

    cmds.delete(old_model, constructionHistory=True)
    cmds.delete(cmds.ls("{0}::*".format(new_model_namespace)))
    cmds.delete(cmds.ls("{0}::*".format(corrective_model_namespace)))

    cmds.parent(old_model, world=True)
    updated_mesh = cmds.rename(old_model, corrective_file.split(".")[0])

    cmds.select(updated_mesh)
    export_file = os.path.join(corrective_path, "{0}_{1}".format(updated_mesh, new_file_suffix))
    cmds.file(export_file, force=True, options="v=0", typ="mayaAscii", exportSelected=True)

    cmds.select(clear=True)

    cmds.file("{0}.ma".format(export_file), open=True, force=True, typ="mayaAscii")

def __invert_shape_with_blendshapes():

    selection = cmds.ls(selection=True)

    if len(selection) != 2:
        om.MGlobal.displayError("Please select only two shapes: first the base shape and then the modified shape.")
        return
    
    base_shape = selection[0]
    inverted_shape = selection[1]

    base_shape_blendshapes = cmds.ls(*cmds.listHistory(base_shape) or [], type= 'blendShape')[0]
    base_shape_skin_cluster = skin.find_related_skin_cluster(base_shape)
    
    cmds.setAttr(attr.name(base_shape_blendshapes, "envelope"), True)
    cmds.select([base_shape, inverted_shape])
    new_inverted_shape = cmds.invertShape()
    cmds.setAttr(attr.name(base_shape_skin_cluster, "envelope"), 0)
    base_shape_duplicated = cmds.duplicate(base_shape)[0]
    base_shape_duplicated_blendshape = cmds.blendShape(new_inverted_shape, base_shape, base_shape_duplicated, frontOfChain=True)[0]
    cmds.setAttr(attr.name(base_shape_duplicated_blendshape, new_inverted_shape), 1)
    cmds.setAttr(attr.name(base_shape_duplicated_blendshape, base_shape), -1)

    delta = cmds.duplicate(base_shape_duplicated, name="delta")[0]
    cmds.parent(delta, world=True)
    cmds.setAttr(attr.name(base_shape_blendshapes, "envelope"), 1)
    cmds.setAttr(attr.name(base_shape_skin_cluster, "envelope"), 1)

    cmds.delete(new_inverted_shape)
    cmds.delete(base_shape_duplicated)

    return delta

def __get_model_from_file(path, file):
    model = None
    namespace = file.split(".")[0]
    full_path = os.path.join(path, file)
    if os.path.isfile(full_path):
        model = cmds.file(full_path, i=True, defaultNamespace=False, namespace=namespace, preserveReferences=False, returnNewNodes=True)
    else:
        raise Exception("File not found: {0}".format(full_path)) 
    
    return namespace, model

if __name__ == "__main__":
    pass
    