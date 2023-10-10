import maya.cmds as cmds
import maya.api.OpenMaya as om
    
def create_joint_under_selected_node(prefix="joint"):
    """Creates a joint as a child of the selected nodes.

    Parameters
    ----------
    prefix : str, optional
        Prefix (name) of the created joint.
    
    Returns
    -------
        No return 
    """
    selection = cmds.ls(selection=True, flatten=True)
    index = 1
    
    if selection:
        for item in selection:
            
            if cmds.nodeType(item) in ["transform", "joint"]:
                pos = cmds.xform(item, query=True, worldSpace=True, pivots=True)
            else:
                pos = cmds.xform(item, query=True, worldSpace=True, translation=True)
            
            cmds.select(item, replace=True)
            cmds.joint(position=[pos[0], pos[1], pos[2]], name = "{0}{1}".format(prefix, index))[0]
            
            index += 1
    else:
        cmds.joint(name = "{0}{1}".format(prefix, index))
    
def create_joint_at_point(prefix="joint"):
    """Creates not connected joints on the positions of the selected nodes.

    Parameters
    ----------
    prefix : str, optional
        Prefix (name) of the created joints.
    
    Returns
    -------
        No return. 
    """
    selection = cmds.ls(selection=True, flatten=True)
    
    if selection:
        for item in selection:
            
            if cmds.nodeType(item) in ["transform", "joint"]:
                pos = cmds.xform(item, query=True, worldSpace=True, pivots=True)
            else:
                pos = cmds.xform(item, query=True, worldSpace=True, translation=True)
            
            cmds.select(clear=True)
            cmds.joint(position=[pos[0], pos[1], pos[2]], name = "{0}1".format(prefix))[0]
    else:
        cmds.joint(name = "{0}1".format(prefix))
        
def create_joint_hierarchy():
    """Creates an hierarchy from siblings joints.

    Parameters
    ----------
    joints : selection
        All the joints that need to be in hierarchy.
    
    Returns
    -------
        No return. 
    """
    selected_items = cmds.ls(orderedSelection=True)
    
    selected_items_len = len(selected_items)
    for index in range(1, selected_items_len+1):
        current_item = selected_items[-index]
        
        if index + 1 <= selected_items_len:
            next_item = selected_items[-index-1]

            cmds.parent(current_item, next_item)

def clean_tip_joints_orientations_by_hierarchy():
    """Zero-out the tip joints orientations from a hierarchy of joints.

    Parameters
    ----------
    joint : selection
        A joint part of the hierarchy to zero-out the tip joints orientation.
    
    Returns
    -------
        No return. 
    """
    selection = cmds.ls(selection=True)[0]
    joints = cmds.listRelatives(selection, allDescendents=True, type="joint")
    clean_tip_joints_orientations(joints)

def clean_tip_joints_orientations_by_selection():
    """Zero-out the tip joints orientations for the selected joints.

    Parameters
    ----------
    joints : selection
        The joints to zero-out the orientations.
    
    Returns
    -------
        No return. 
    """
    selection = cmds.ls(selection=True, type="joint")
    clean_tip_joints_orientations(selection)

def clean_tip_joints_orientations(joints):
    """Zero-out the tip joints orientations for the input joints.

    Parameters
    ----------
    joints : list
        The joints to zero-out the orientations.
    
    Returns
    -------
        No return. 
    """
    for jnt in joints:
        children = cmds.listRelatives(jnt, children=True, type="joint")
        if not children:
            cmds.setAttr("{0}.jointOrientX".format(jnt), 0)
            cmds.setAttr("{0}.jointOrientY".format(jnt), 0)
            cmds.setAttr("{0}.jointOrientZ".format(jnt), 0)

def get_aim_axis(joint_name):
    """Get the aim axis of a joint in a chain.

    Parameters
    ----------
    joint_name : str
        Joint name.
    
    Returns
    -------
        str:
            The description of the axis. Ex: "-x".
    """
    child_joint = cmds.listRelatives(joint_name, children=True)

    if not child_joint:
        om.MGlobal.displayError('{0} does not have any children to check the aim axis'.format(joint_name))
        return False
    
    child_joint = child_joint[0]

    axes = ['x', 'y', 'z']
    translation = (
        cmds.getAttr('{}.translateX'.format(child_joint)),
        cmds.getAttr('{}.translateY'.format(child_joint)),
        cmds.getAttr('{}.translateZ'.format(child_joint)),
    )
    absolute_translation = (
        abs(translation[0]),
        abs(translation[1]),
        abs(translation[2])
    )

    max_axis_value = max(max(absolute_translation[0], absolute_translation[1]), absolute_translation[2])

    for idx in range(len(absolute_translation)):
        if max_axis_value == absolute_translation[idx]:
            axis_tmp = axes[idx]
            if translation[idx] < 0.0:
                axis = ('-{}'.format(axis_tmp))
            else:
                axis = axis_tmp
    return axis

def replace_joints_from_locators(aim_vector, up_vector):
    """Replace the selected joint chain to a new joint chain where the joints will be oriented to be in the same plane (required for IK). Select first the joints that should be replaced and then the locators with the new positions.

    Parameters
    ----------
    joints: selection
        The joints that will be replaced (first selected, in the hierarchy order). TODO: Could be improved and require only the root joint.
    locators: selection
        The locators representing the new positions (second selected, in the same order as the joints).
    aim_vector : lst
        List with the new joint chain aim vector values. Ex. [1, 0, 0].
    up_vector : str
        List with the plane up vector values. Ex. [0, -1, 0].
    
    Returns
    -------
        no return. 
    """
    locators, joints = __get_selection()
    cmds.select(clear = True)
    
    root_joint = joints[0]
    last_joint = joints[len(joints) - 1]
    
    parent_joint = cmds.listRelatives(root_joint, parent=True)
    children_joints = cmds.listRelatives(last_joint, children=True)
    
    __unparent_joints_and_children(joints, children_joints)
    
    cmds.delete(root_joint)
    
    __create_joint_chain_from_locators(locators = locators, 
                                      joints_names = joints, 
                                      aim_vector = aim_vector, 
                                      up_vector = up_vector,
                                      world_up_vector = __get_plane_normal(*locators))
    
    if parent_joint is not None:
        cmds.parent(root_joint, parent_joint)
    
    if children_joints is not None:
        for child in children_joints:
            cmds.parent(child, last_joint)
            
def create_joint_chain_from_locators_by_selection(aim_vector, up_vector):
    """Creates a joint chain where the joints will be oriented to be in the same plane (required for IK) from the selected locators.

    Parameters
    ----------
    aim_vector : lst
        List with the new joint chain aim vector values. Ex. [1, 0, 0].
    up_vector : str
        List with the plane up vector values. Ex. [0, -1, 0].
    
    Returns
    -------
        no return. 
    """
    locators = cmds.ls(orderedSelection=True, flatten=True)
    
    __create_joint_chain_from_locators(locators = locators, 
                                      aim_vector = aim_vector, 
                                      up_vector = up_vector,
                                      world_up_vector = __get_plane_normal(*locators))

def toggle_axis_visibility_on_selected():
    """Toggle axis visibility on the joints.

    Parameters
    ----------
    joints : selection
        Selected joints
    
    Returns
    -------
        no return. 
    """
    selected_joints = cmds.ls(selection=True)
    
    if not selected_joints:
        om.MGlobal.displayWarning("Select at least one joint.")
        return
        
    __toggle_axis_visibility(selected_joints)

def toggle_axis_visibility_on_hierarchy():
    """Toggle axis visibility on a joint hierarchy.

    Parameters
    ----------
    joints : selection
        Selected joints
    
    Returns
    -------
        no return. 
    """
    joints = __get_all_joints_in_hierarchy() 
    
    if not joints:
        om.MGlobal.displayWarning("Select at least one joint.")
        return
        
    __toggle_axis_visibility(joints)

def parent_constrain_in_hierarchy(driver, driven):
    """Parent constrain a hierarchy of objects to another hierarchy of objects matching their names.

    Parameters
    ----------
    driver : str
        Root of the driver object.
    driven : str
        Root of the driven object.
    
    Returns
    -------
        no return. 
    """
    driver_nodes = cmds.listRelatives(driver, allDescendents=True)
    driven_nodes = cmds.listRelatives(driven, allDescendents=True)
    driver_nodes.append(driver)
    driven_nodes.append(driven)
    driven_idx = 0
    
    for driver_node in driver_nodes:
        
        if cmds.nodeType(driver_node) != "joint":
            print("Not joint: {0} ({1})".format(driver_node, cmds.nodeType(driver_node)))
            continue
            
        for driven_node in driven_nodes:
            
            if cmds.nodeType(driven_node) != "joint":
                continue
            
            driver_node_name = driver_node.split("_")[1]
            driven_node_name = driven_node.split("_")[1]
            
            if driver_node_name == driven_node_name:
                cmds.parentConstraint(driver_node, driven_node)
                break    

def parent_constrain_in_ordered_hierarchy(driver, driven):
    """Parent constrain a hierarchy of objects to another hierarchy of objects by their position on the hierarchy.

    Parameters
    ----------
    driver : str
        Root of the driver object.
    driven : str
        Root of the driven object.
    
    Returns
    -------
        no return. 
    """
    driver_nodes = cmds.listRelatives(driver, allDescendents=True, type="joint")
    driven_nodes = cmds.listRelatives(driven, allDescendents=True, type="joint")
    driver_nodes.append(driver)
    driven_nodes.append(driven)
    
    for idx, driver_node in enumerate(driver_nodes):
        cmds.parentConstraint(driver_node, driven_nodes[idx])        

def __get_all_joints_in_hierarchy():
    
    hierarchy_and_selected_joints = []
    
    selected_joints = cmds.ls(selection=True)
    all_joints_in_hierarchy = cmds.ls(cmds.listRelatives(type="joint", allDescendents=True))
    
    hierarchy_and_selected_joints.extend(all_joints_in_hierarchy)
    hierarchy_and_selected_joints.extend(selected_joints)
    
    return hierarchy_and_selected_joints

def __get_local_axis_attr_name(joint):
    return "{0}.{1}".format(joint, "displayLocalAxis")

def __toggle_axis_visibility(joints):
    first_joint_local_axis_visible = cmds.getAttr(__get_local_axis_attr_name(joints[0]))
    
    for joint in joints:
        cmds.setAttr(__get_local_axis_attr_name(joint), not first_joint_local_axis_visible)

def __unparent_joints_and_children(joints, children_joints):
    if cmds.listRelatives(joints[0], parent=True) is not None:
        cmds.parent(joints[0], world=True)
 
    if children_joints:   
        for child in children_joints:
            cmds.parent(child, world=True)

def __create_joint_chain_from_locators(locators, aim_vector, up_vector, world_up_vector, joints_names = None):

    cmds.select(clear = True)
    
    joints_names = __get_names(locators, joints_names)
    
    for idx, loc in enumerate(locators):
        pos = cmds.xform(loc, query=True, worldSpace=True, translation=True)
        name = joints_names[idx]
        cmds.select(clear = True)
        cmds.joint(name = name, position = [pos[0], pos[1], pos[2]])
    
    __aim_joint_to_next_joint(joints_names, aim_vector, up_vector, world_up_vector)
    __reparent_joints(joints_names) 
    __clean_joints_rotations(locators, joints_names)
    __re_aim_after_cleaning_rotations(locators, joints_names, aim_vector, up_vector, world_up_vector)

def __re_aim_after_cleaning_rotations(locators, names, aim_vector, up_vector, world_up_vector):
    
    aim_constraints = []
    
    for idx in range(0, len(names) - 1):
        aim_constraints.append(cmds.aimConstraint(locators[idx + 1], names[idx], aimVector=aim_vector, upVector=up_vector, worldUpVector=world_up_vector))
        
    aim_constraints.append(cmds.aimConstraint(locators[-1*(len(names)-1)], 
                                              names[-1*(len(names)-2)], 
                                              aimVector=[aim_vector[0]*-1, aim_vector[1]*-1, aim_vector[2]*-1], 
                                              upVector=up_vector, 
                                              worldUpVector=world_up_vector))
                   
    for const in aim_constraints:
        cmds.delete(const)

def __clean_joints_rotations(locators, names):
    for idx, loc in enumerate(locators):
        name = names[idx]
        cmds.setAttr("{0}.jointOrientX".format(name), 0)
        cmds.setAttr("{0}.jointOrientY".format(name), 0)
        cmds.setAttr("{0}.jointOrientZ".format(name), 0)
        cmds.setAttr("{0}.rotateX".format(name), 0)
        cmds.setAttr("{0}.rotateY".format(name), 0)
        cmds.setAttr("{0}.rotateZ".format(name), 0)

def __reparent_joints(names):
    for idx in range(1, len(names)):
        cmds.parent(names[-idx], names[-idx-1])

def __aim_joint_to_next_joint(names, aim_vector, up_vector, world_up_vector):
    
    aim_constraints = []
    
    for idx in range(1, len(names)):
        aim_constraints.append(cmds.aimConstraint(names[-idx], names[-idx-1], aimVector=aim_vector, upVector=up_vector, worldUpVector=world_up_vector))
        
    aim_constraints.append(cmds.aimConstraint(
                           names[-1*(len(names)-1)], 
                           names[-1*(len(names)-2)], 
                           aimVector = [aim_vector[0]*-1, aim_vector[1]*-1, aim_vector[2]*-1],
                           upVector = up_vector, 
                           worldUpVector=world_up_vector))
        
    for const in aim_constraints:
        cmds.delete(const)

def __get_names(locators, names):
    if names is None:
        names = []
        for loc in locators:
            names.append(__get_joint_name(loc))
    return names

def __get_selection():
    
    selection = cmds.ls(orderedSelection=True, flatten=True)
    
    locators = []
    joints = []
    
    if len(selection) %2 != 0:
        raise Exception("The number of locators and joints should be the same.")
    
    for idx in range(0, int(len(selection)/2)):
        if cmds.nodeType(selection[idx]) != "joint":
            raise Exception("Please select the joints first.")
        joints.append(selection[idx])
    
    for idx in range(int(len(selection)/2), len(selection)):
        locators.append(selection[idx])
        
    return locators, joints
    
def __get_joint_name(loc_name):
    return "{0}_jnt".format(loc_name)

def __get_plane_normal(locator1, locator2, locator3):
    loc1_vec = om.MVector(cmds.xform(locator1, query = True, worldSpace = True, translation = True))
    loc2_vec = om.MVector(cmds.xform(locator2, query = True, worldSpace = True, translation = True))
    loc3_vec = om.MVector(cmds.xform(locator3, query = True, worldSpace = True, translation = True))
    
    plane_vec1 = loc1_vec - loc3_vec
    plane_vec2 = loc1_vec - loc2_vec
    
    cross_product = plane_vec1 ^ plane_vec2
    plane_normal = cross_product.normalize()
    
    return plane_normal

if __name__ == "__main__":
    print(get_aim_axis("joint1"))