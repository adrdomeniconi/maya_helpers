import maya.cmds as cmds
import maya.api.OpenMaya as om

def parent_shapes():
    """Parent the selected shapes under the target transform. Select first the shapes and lastly the transform.

    Parameters
    ----------
    sources_shapes: selection
        One or more shapes.
    target_transform: selection
        Name of the target transform.

    Returns
    -------
        No return.
    """
    selection = cmds.ls(selection=True)
    
    if len(selection) < 2:
        om.MGlobal.displayError("Select at least two transforms.")
        return
        
    target = selection[-1]
    sources = selection[:-1]
    
    for source in sources:
        shapes = cmds.listRelatives(source, shapes=True, children=True, fullPath=True)
        for child_shape in shapes:
            cmds.parent(child_shape, target, shape=True, relative=True)
    
    for source in sources:
        cmds.delete(source)

def recolor_shapes_by_selection(color_id): 
    """Recolor the shapes of the selected transforms.

    Parameters
    ----------
    transform: selection
        One or more transforms.
    color_id: int
        Maya index of the desired color.

    Returns
    -------
        No return.
    """
    selection = cmds.ls(selection=True) 
    for transform in selection:
        recolor_shapes(transform, color_id)   
    
def recolor_shapes(transform, color_id):
    """Recolor the selected shapes of the input transform.

    Parameters
    ----------
    transform: str
        One or more transform.
    color_id: int
        Maya index of the desired color.

    Returns
    -------
        No return.
    """
    shapes = cmds.ls(cmds.listRelatives(transform, allDescendents=True, shapes=True))
    for shape in shapes:
        cmds.setAttr("{0}.overrideEnabled".format(shape), True) 
        cmds.setAttr("{0}.overrideRGBColors".format(shape), False) 
        cmds.setAttr("{0}.overrideColor".format(shape), color_id) 

def rotate_cvs(transform, angle):
    """Rotate the cvs of all the input transform shapes.

    Parameters
    ----------
    transform: str
        A transform with shapes.
    angle: tuple
        Rotation angle in degrees. Ex. (0, 90, 0)

    Returns
    -------
        No return.
    """
    __select_all_shapes_cvs(transform)
    cmds.xform(rotation=[angle[0],angle[1],angle[2]], objectSpace=True)
    cmds.select(clear=True)

def translate_cvs(transform, translation):
    """Translate the cvs of all the input transform shapes.

    Parameters
    ----------
    transform: str
        A transform with shapes.
    translation: tuple
        Vector to translate. Ex. (10, 10, 0).

    Returns
    -------
        No return.
    """
    __select_all_shapes_cvs(transform)
    cmds.move(translation[0], translation[1], translation[2], relative=True, objectSpace=True, worldSpaceDistance=True)
    cmds.select(clear=True)

def scale_shapes(transform, factor = None):
    """Scale the cvs of all the input transform shapes.

    Parameters
    ----------
    transform: str
        A transform with shapes.
    factor: int or list
        Factor or Vector to translate. Ex. (10, 5, 0) or 5 (in this case it will be handled as (5,5,5))

    Returns
    -------
        No return.
    """
    if not isinstance(factor, list):
        factor = [factor, factor, factor]

    original_pivot = cmds.xform(transform, translation=True, query=True, worldSpace=True)

    __select_all_shapes_cvs(transform)
    scale_pivot = find_middle_point()

    cmds.xform(transform, pivots=scale_pivot, worldSpace=True)
    cmds.xform(scale=[factor[0], factor[1], factor[2]], worldSpace=True)
    cmds.xform(transform, pivots=original_pivot, worldSpace=True)

    cmds.select(clear=True)

def orient_transform_keeping_the_shape(transform, orientation=None, scale=None, parent_level=0):
    """Change the transform keeping the shapes on their original position.

    Parameters
    ----------
    transform: str
        A transform with shapes.
    orientation: tuple, optional
        Orientation change in degrees. Ex. (0, 90, 0)
    scale: tuple, optional
        Scale change in units. Ex. (2, 2, 2)
    parent_level:
        If the transformation should be applied to a parent of the input transform input this field with the desired parenting level.

    Returns
    -------
        No return.
    """
    shapes = cmds.listRelatives(transform, children=True, shapes=True)
    transform_to_change = transform

    for idx in range(parent_level):
        transform_to_change = cmds.listRelatives(transform_to_change, parent=True)[0]

    all_original_shapes_pvs = []

    for shape in shapes:
        original_pv_pos = []
        original_shape_pvs = cmds.ls('{0}.cv[:]'.format(shape), flatten=True )
        for pv in original_shape_pvs:
            original_pv_pos.append([pv, cmds.xform(pv, query=True, worldSpace=True, translation=True)])
        all_original_shapes_pvs.append(original_pv_pos)
    
    if orientation is not None:
        cmds.setAttr("{0}.rx".format(transform_to_change), orientation[0])
        cmds.setAttr("{0}.ry".format(transform_to_change), orientation[1])
        cmds.setAttr("{0}.rz".format(transform_to_change), orientation[2])
    
    if scale is not None:
        cmds.setAttr("{0}.sx".format(transform_to_change), scale[0])
        cmds.setAttr("{0}.sy".format(transform_to_change), scale[1])
        cmds.setAttr("{0}.sz".format(transform_to_change), scale[2])

    for original_pv_pos in all_original_shapes_pvs:
        for pv_pos in original_pv_pos:
            cmds.xform(pv_pos[0], worldSpace=True, translation=pv_pos[1])

def find_middle_point_from_selection():
    """Find the middle point of the bounding box around the selected objects.

    Parameters
    ----------
    objects: selection
        A list of objects (can be transforms, shapes, vertices...).
        
    Returns
    -------
        tuple:
            A tuple representing the middle point vector.
    """
    selection = cmds.ls(selection=True)
    bounding_box = cmds.exactWorldBoundingBox(selection)
    centerX = (bounding_box[0] + bounding_box[3]) / 2.0
    centerY = (bounding_box[1] + bounding_box[4]) / 2.0
    centerZ = (bounding_box[2] + bounding_box[5]) / 2.0
    bounding_box_center = [centerX, centerY, centerZ]

    return bounding_box_center

def find_middle_point(transforms):
    """Find the middle point of the bounding box around the selected objects.

    Parameters
    ----------
    trasnform: list
        A list of objects (can be transforms, shapes, vertices...).
        
    Returns
    -------
        tuple:
            A tuple representing the middle point vector.
    """
    bounding_box = cmds.exactWorldBoundingBox(transforms)
    centerX = (bounding_box[0] + bounding_box[3]) / 2.0
    centerY = (bounding_box[1] + bounding_box[4]) / 2.0
    centerZ = (bounding_box[2] + bounding_box[5]) / 2.0
    bounding_box_center = [centerX, centerY, centerZ]

    return bounding_box_center

def __select_all_shapes_cvs(transform):
    cmds.select(clear=True)
    shapes = cmds.listRelatives(transform, children=True, shapes=True)
    for shape in shapes:
        cvs = cmds.ls( '{0}.cv[:]'.format(shape), flatten=True )
        for cv in cvs:
            cmds.select(cv, add=True)

if __name__ == "__main__":
    parent_shapes()