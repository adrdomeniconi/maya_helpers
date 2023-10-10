import maya.cmds as cmds
import maya.mel as mel
import attributes_helpers as attr

def create_pose_interpolator(driver, name="poseInterpolator1", create_neutral_poses=False, driver_twist_axis="x", enable_translation=False, enable_rotation=True, allow_negative_weights=True, driver_controllers=[]):
    """Creates a pose interpolator. 

    Parameters
    ----------
    driver: str
        The driver control, or object that will drive the pose interpolator.
    name: str
        Name of the pose interpolator.
    create_neutral_poses: bool, optional
        If set to True the pose interpolator will be created considering the current pose of the driver as the default pose.
    driver_twist_axis: str, optional
        The driver twist axis. Ex: "x"
    enable_translation: bool, optional
        If set to True the pose interpolator will track translations.
    enable_rotation: bool, optional
        If set to True the pose interpolator will track rotations.
    allow_negative_weights: bool, optional
        If set to True the pose interpolator will consider negative values.
    driver_controllers: list, optional
        List of the controllers and channels that will be modifying the driver of the pose interpolator. Ex: ["hand_fk_ctrl.rx", "hand_fk_ctrl.ry"]
    
    Returns
    -------
        str:
            Pose interpolator name.
    """
    flag_driver_twist_axis = 0
    if driver_twist_axis == "y":
        flag_driver_twist_axis = 1
    elif driver_twist_axis == "z":
        flag_driver_twist_axis = 2
        
    flag_create_neutral_poses = 1 if create_neutral_poses else 0
    cmds.select(driver)
    pose_interpolator_name = mel.eval('createPoseInterpolatorNode("{0}", {1}, {2})'.format(name, flag_create_neutral_poses, flag_driver_twist_axis))
    cmds.select(clear=True)

    cmds.setAttr("{0}Shape.{1}".format(name, "enableTranslation"), enable_translation)
    cmds.setAttr("{0}Shape.{1}".format(name, "enableRotation"), enable_rotation)
    cmds.setAttr("{0}Shape.{1}".format(name, "allowNegativeWeights"), allow_negative_weights)

    for idx, controller in enumerate(driver_controllers):
        cmds.connectAttr(controller, attr.name("{0}Shape.driver[0]".format(pose_interpolator_name), "driverController[{0}]".format(idx)))

    return pose_interpolator_name

def create_pose(pose_interpolator_name, name="pose1", poseType="swing", blendshape=None, blendshape_target=None, trigger_values=[]):
    """Creates a pose. 

    Parameters
    ----------
    pose_interpolator_name: str
        Name of the pose interpolator that will be tracking this pose
    name: str
        Name of the pose.
    poseType: str
        Valid pose types: "swingandtwist", "swing", "twist"
    blendshape: str, optional
        The name of a blendshape node. If informed, the pose with be connected to the blendshape node and controlled by the pose interpolator.
    blendshape_target: str, optional
        Name of the blendshape attribute that should be connected to this pose.
    trigger_values: list, optional
        Controller values that will define the pose. Ex: [["upperLeg_L_fk_ctrl.ry", 30], ["lowerLeg_L_fk_ctrl.ry", 45]]
    
    Returns
    -------
        str:
            The created pose index.
    """
    original_controller_values = []
    for controller_value in trigger_values:
        original_controller_values.append(cmds.getAttr(controller_value[0]))
        cmds.setAttr(controller_value[0], controller_value[1])

    pose_index = mel.eval('poseInterpolatorAddShapePose("{0}", "{1}", "{2}", {3}, {4})'.format(pose_interpolator_name, name, poseType, "{}", 0))
    
    for idx, controller_value in enumerate(trigger_values):
        cmds.setAttr(controller_value[0], original_controller_values[idx])

    if blendshape is not None and blendshape_target is not None:
        cmds.connectAttr(attr.name(pose_interpolator_name, "output[{0}]".format(pose_index)), attr.name(blendshape, blendshape_target))
                
    return pose_index

def create_combined_pose(pose_interpolator1, pose_index1, pose_interpolator2, pose_index2, name="combinedPose1", blendshape=None, blendshape_target=None):
    """Triggers a blendshape based on two different poses. 

    Parameters
    ----------
    pose_interpolator1: str
        Pose interpolator of the first pose. 
    pose_index1: str
        Index of the pose.
    pose_interpolator2: str
        Pose interpolator of the first pose. 
    pose_index2: str
        Index of the pose.
    name: str, optional
        Name of the combined pose. It will applied to a multiply node.
    blendshape: str, optional
        The name of a blendshape node. If informed, the pose with be connected to the blendshape node and controlled by the pose interpolator.
    blendshape_target: str, optional
        Name of the blendshape attribute that should be connected to this pose.
    
    Returns
    -------
        No return.
    """
    combine_node = cmds.createNode("multiplyDivide", name="{0}_multi".format(name))
    cmds.connectAttr(attr.name(pose_interpolator1, "output[{0}]".format(pose_index1)), attr.name(combine_node, "input1X"))
    cmds.connectAttr(attr.name(pose_interpolator2, "output[{0}]".format(pose_index2)), attr.name(combine_node, "input2X"))
    cmds.connectAttr(attr.name(combine_node, "outputX"), attr.name(blendshape, blendshape_target))
            
if __name__ == "__main__":
    
    pi_name = create_pose_interpolator(
        "jaw_ctrl",
        name="jaw_poseInterpolator",
        create_neutral_poses=True,
        driver_twist_axis=False,
        enable_translation=False,
        allow_negative_weights=False,
        driver_controllers=[attr.name("jaw_ctrl", "rx"), attr.name("jaw_ctrl", "ry"), attr.name("jaw_ctrl", "rz")]
    )

    pose_idx = create_pose(pi_name,
                name="open_jaw",
                poseType="swing",
                blendshape="blendShape5",
                blendshape_target="jaw_ctrl_open_inv",
                trigger_values = [[attr.name("jaw_ctrl", "rz"), -40]])