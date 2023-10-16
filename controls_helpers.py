import maya.cmds as cmds
import maya.api.OpenMaya as om
import attributes_helpers as attr

def mirror_ctrls_values(invert_translation=False):
    """Copy all default attributes (translation, rotation, scale) and all custom attributes to a mirrored node control.

    Parameters
    ----------
    source_ctrls : selection
        Source nodes to be mirrored
    invert_translation: False, optional
        If set to True it will invert the direction of the translation attributes.

    Returns
    -------
    no return
    """
    selection = cmds.ls(orderedSelection=True)
    side_tag = None
    mirror_tag = None

    if len(selection) < 1:
        raise Exception("Please select at least one control in order to mirror.")

    for ctrl in selection:
        if ctrl.upper().find("_L_") > -1:
            side_tag = "L"
            mirror_tag = "R"
        elif ctrl.upper().find("_R_") > -1:
            side_tag = "R"
            mirror_tag = "L"
        else:
            om.MGlobal.displayWarning("{0} could not be mirrored. Couldn't find the side identifier.".format(ctrl))
            continue
        
        mirror_ctrl = ctrl.replace("_{0}_".format(side_tag), "_{0}_".format(mirror_tag))
        
        if cmds.objExists(mirror_ctrl):
            attr.copy_attrs_values(ctrl, mirror_ctrl, invert_translation=invert_translation)
        else:
            om.MGlobal.displayWarning("{0} could not be mirrored. Couldn't find the mirror control.".format(mirror_ctrl))
            continue

def print_modified_ctrls(ctrl_suffix="_ctrl"):
    """Print all controls that have attributes with values different than zero.

    Parameters
    ----------
    ctrl_suffix : str
        Suffix to identify nodes that are controls.

    Returns
    -------
    no return
    """
    transforms = cmds.ls(type="transform")
    attrs = ["tx", "ty", "tz", "rx", "ry", "rz"]
    modified_ctrls = []
    for transform in transforms:
        if transform.endswith(ctrl_suffix):
            for attr in attrs:
                attr_value = cmds.getAttr("{0}.{1}".format(transform, attr))
                if attr_value != 0:
                    modified_ctrls.append([transform, attr_value])

    print(modified_ctrls)

def select_all_ctrls(ctrl_suffix = "*_ctrl"):
    """Select all controls based on the informed suffix

    Parameters
    ----------
    ctrl_suffix : str
        Suffix to identify nodes that are controls.

    Returns
    -------
    no return
    """
    all_ctrls = cmds.ls(ctrl_suffix)
    cmds.select(all_ctrls, replace=True)

if __name__ == "__main__":
    mirror_ctrls_values()
    

    