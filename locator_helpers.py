import maya.cmds as cmds
import maya.api.OpenMaya as om
    
def create_locator_at_point(match_rotation=False, name=None):
    """Create a locator on a selected point (can be a transform or a CV).

    Parameters
    ----------
    selected_point: selection
        The point to be created the locator
    match_rotation : bool, optional
        If set to true the created locator will match the rotation of the selected transform.
    name : str, optional
        The name of the created locator.
    
    Returns
    -------
        no return.
    """
    selection = cmds.ls( orderedSelection=True, flatten=True)
    
    if selection:
        for item in selection:
            
            if cmds.nodeType(item) in ["transform", "joint"]:
                translation = cmds.xform(item, query=True, worldSpace=True, pivots=True)
            else:
                translation = cmds.xform(item, query=True, worldSpace=True, translation=True)
                
            new_loc = cmds.spaceLocator(name=name, position=[0.0, 0.0, 0.0])[0]
            cmds.setAttr("{0}.translate".format(new_loc), translation[0], translation[1], translation[2])
            
            if match_rotation:
                rotation = cmds.xform(item, query=True, worldSpace=True, rotation=True)
                cmds.setAttr("{0}.rotate".format(new_loc), rotation[0], rotation[1], rotation[2])
    else:
        cmds.spaceLocator(position=[0.0, 0.0, 0.0])

def create_locator_at_the_center(objects = None):
    """Create a locator on the center of the selected points (can be transforms or CVs).

    Parameters
    ----------
    objects : list/selection
        If null it will use the selected objects as inputs.
    
    Returns
    -------
        no return.
    """
    if objects is None:
        objects = cmds.ls(selection=True, flatten=True)

    if objects:
        bbx = cmds.exactWorldBoundingBox(objects)
        centerX = (bbx[0] + bbx[3]) / 2.0
        centerY = (bbx[1] + bbx[4]) / 2.0
        centerZ = (bbx[2] + bbx[5]) / 2.0
        bbox_center = [centerX, centerY, centerZ]
        loc = cmds.spaceLocator()[0]
        cmds.setAttr('{}.translate'.format(loc), *bbox_center)
        cmds.select(loc)
        
        return loc
    else:
        return cmds.spaceLocator()

def create_locator_based_on_selection():
    """Create a locator on a selected point OR on the center of the selected points (can be transforms or CVs), depending on the number of selected objects.

    Parameters
    ----------
    selected_points: selection
        The point to be created the locator or if many to be created a centered locator.
    
    Returns
    -------
        no return.
    """
    selection_lenght = len(cmds.ls(selection=True, flatten=True))
    
    if selection_lenght == 1:
        create_locator_at_point()
    elif selection_lenght > 1:
        create_locator_at_the_center()
    else:
        cmds.spaceLocator()
        
def create_locator_at_one_third():
    """Create a locator on on third between the two selected points (can be transforms or CVs).

    Parameters
    ----------
    object1 : selection
        First object
    object2 : selection
        Second object
    
    Returns
    -------
        no return.
    """
    selection = cmds.ls(orderedSelection=True)
    
    first_position = __get_translation(selection[0])
    last_position = __get_translation(selection[1])
    
    first_position_vec = om.MVector(first_position)
    last_position_vec = om.MVector(last_position)
    
    final_position_vec = first_position_vec + ((last_position_vec - first_position_vec)/3) 
        
    new_loc = cmds.spaceLocator(position=[0.0, 0.0, 0.0])[0]
    cmds.setAttr("{0}.translate".format(new_loc), final_position_vec[0], final_position_vec[1], final_position_vec[2])
      
def clear_local_position(locators):
    """Clear the local position of all the input locators.

    Parameters
    ----------
    locators : list
        List of locators.
    
    Returns
    -------
        no return.
    """
    for loc in locators:
        tx = cmds.getAttr("{0}.{1}".format(loc, "tx"))
        ty = cmds.getAttr("{0}.{1}".format(loc, "ty"))
        tz = cmds.getAttr("{0}.{1}".format(loc, "tz"))
        
        local_position_x = cmds.getAttr("{0}.{1}".format(loc, "localPositionX"))
        local_position_y = cmds.getAttr("{0}.{1}".format(loc, "localPositionY"))
        local_position_z = cmds.getAttr("{0}.{1}".format(loc, "localPositionZ"))
        
        cmds.setAttr("{0}.{1}".format(loc, "tx"), tx + local_position_x)
        cmds.setAttr("{0}.{1}".format(loc, "ty"), ty + local_position_y)
        cmds.setAttr("{0}.{1}".format(loc, "tz"), tz + local_position_z)
        
        cmds.setAttr("{0}.{1}".format(loc, "localPositionX"), 0)
        cmds.setAttr("{0}.{1}".format(loc, "localPositionY"), 0)
        cmds.setAttr("{0}.{1}".format(loc, "localPositionZ"), 0)
   
def __get_translation(node):
    
    if cmds.nodeType(node) in ["transform", "joint"]:
        translation = cmds.xform(node, query=True, worldSpace=True, pivots=True)
    else:
        translation = cmds.xform(node, query=True, worldSpace=True, translation=True)
        
    return [translation[0], translation[1], translation[2]]

if __name__ == "__main__":
    create_locator_at_one_third()