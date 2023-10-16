import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om

default_attrs = ['tx','ty','tz','rx','ry','rz','sx','sy','sz','v']

def name(node, attr_name):
    """Format node and attribute name in a format expected by Maya.

    Parameters
    ----------
    node : str
        Node name
    attr_name : str
        Attribute name

    Returns
    -------
    str
        a formated node and attribute name
    """
    return "{0}.{1}".format(node, attr_name)
    
def hide_and_lock_attr(node, attr_name, hide_and_lock=True):
    """Hide and lock a channel box attribute

    Parameters
    ----------
    node : str
        Node name
    attr_name : str
        Attribute name
    hide_and_lock: bool, optional
        Define is the attribute should be hided and locked or unhided and unlocked.

    Returns
    -------
    no return
    """
    cmds.setAttr(name(node, attr_name), keyable=not hide_and_lock, lock=hide_and_lock)

def copy_selected():
    """Copy a custom channel box attribute to a another node.

    Parameters
    ----------
    target_node : selection
        Select first the target object to copy the attribute.
    source_node : selection
        Select the target node and the channel box attribute that you want to be copied.

    Returns
    -------
    no return
    """
    selection = cmds.ls(selection=True)
    
    if not __validate_selection(selection):
        om.MGlobal.displayError("You need to select exactly two objects.")
        return
    
    selected_attrs = __get_channel_box_selected_attributes()
    if not selected_attrs:
        om.MGlobal.displayError("Select at least one attribute on the channel box.")
        return
    
    target_node = selection[0]
    
    if(__is_copy_to_same_object(selection)):
        source_node = selection[0]
    else:
        source_node = selection[1]
    
    for attr in selected_attrs:
        attr_type = cmds.attributeQuery( attr, node=source_node, attributeType=True )
        if not __valid_attribute(attr_type):
            om.MGlobal.displayError("Attribute not supported: {0}".format(attr))
        else:
            __copy_attribute(source_node, target_node, attr)

def proxy_selected():
    """Proxy a custom channel box attribute to a another node.

    Parameters
    ----------
    target_node : selection
        Select first the target object to proxy the attribute.
    source_node : selection
        Select the target node and the channel box attribute that you want to be proxied.

    Returns
    -------
    no return
    """
    selection = cmds.ls(selection=True)

    if not __validate_selection(selection):
        om.MGlobal.displayError("You need to select exactly two objects.")
        return
    
    selected_attrs = __get_channel_box_selected_attributes()
    if not selected_attrs:
        om.MGlobal.displayError("Select at least one attribute on the channel box.")
        return
        
    source_node = selection[1]
    target_node = selection[0]
    
    cmds.select(target_node, replace=True)
    
    for attr in selected_attrs:
        cmds.addAttr(longName = attr, proxy=name(source_node, attr))
            
def lock_and_hide_all_attributes():
    """Hide and lock all attributes

    Parameters
    ----------
    node : selection
        Target node

    Returns
    -------
    no return
    """
    selection = cmds.ls(selection=True)
    
    if not selection:
        om.MGlobal.displayError("Select at least one transform object.")
        return
    
    for node in selection:
        attrs = cmds.listAttr(node, keyable=True)
        
        if not attrs:
            continue
            
        for attr in attrs:
            hide_and_lock_attr(node, attr)

def restore_default_attributes_visibility_from_selection():
    """Unhide and unlock all default channelbox attributes

    Parameters
    ----------
    node : selection
        Target node

    Returns
    -------
    no return
    """
    selection = cmds.ls(selection=True)
    
    if not selection:
        om.MGlobal.displayError("Select at least one transform object.")
        return
    
    for node in selection:
        for attr in default_attrs:
            hide_and_lock_attr(node, attr, hide_and_lock=False)
  
def restore_default_attributes_visibility(node):
    """Unhide and unlock all default channelbox attributes

    Parameters
    ----------
    node : str
        Target node

    Returns
    -------
    no return
    """
    for attr in default_attrs:
        hide_and_lock_attr(node, attr, hide_and_lock=False)

def create_divider_by_selection(divider_label):
    """Create a channel box divider

    Parameters
    ----------
    divider_label : str
        Label that will be shown on the divider
    node: selection
        Node to be added the divider.

    Returns
    -------
    no return
    """
    selection = cmds.ls(selection=True)
    
    if not selection:
        om.MGlobal.displayError("Please select one transform.")
        return
    
    create_divider(divider_label, selection[0])

def create_divider(divider_label, node):
    """Create a channel box divider

    Parameters
    ----------
    divider_label : str
        Label that will be shown on the divider
    node: str
        Node to be added the divider.

    Returns
    -------
    no return
    """
    if cmds.objExists(divider_label):
        om.MGlobal.displayError('{} already exists'.format(divider_label))
        return
    
    cmds.select(node)
        
    __create_attribute_enum(node, "enum", divider_label, "----------", 0, "{0}:".format(divider_label))
    __set_attribute_access(name(node, divider_label), True, False)

def copy_attrs_values(source, target, custom_attrs_suffixes=["_attr", "_attr_proxy", "_proxy_attr"], invert_translation = False):
    """Copy all default attributes (translation, rotation, scale) and all custom attributes to another node.

    Parameters
    ----------
    source : str
        Source node
    target: str
        Target node
    custom_attrs_suffixes: list, optional
        List of all preffixes used in custom attributes
    invert_translation: False, optional
        If set to True it will invert the direction of the translation attributes.

    Returns
    -------
    no return
    """
    base_attrs = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]
    all_attrs = [attr for attr in cmds.listAttr(source)]
    custom_attrs = []
    for attr in all_attrs:
        for attr_sufix in custom_attrs_suffixes:
            if attr.endswith(attr_sufix):
                custom_attrs.append(attr) 
                break
    relevant_attrs = base_attrs + custom_attrs
    
    for attr in relevant_attrs:
        source_value = cmds.getAttr("{0}.{1}".format(source, attr))
        
        if invert_translation and attr in ["tx", "ty", "tz"]:
            source_value = -source_value
        
        if not cmds.objExists("{0}.{1}".format(target, attr)):
            if attr.find("_L_") > 0:
                attr = attr.replace("_L_", "_R_")
            elif attr.find("_R_") > 0:
                attr = attr.replace("_R_", "_L_")

        if cmds.objExists("{0}.{1}".format(target, attr)) and cmds.getAttr("{0}.{1}".format(target, attr), settable=True):
            cmds.setAttr("{0}.{1}".format(target, attr), source_value)

def print_all_custom_fields_default_values(suffix = "*_ctrl"):
    """Print all the custom fields default values for the controls (or the desired nodes). This is a supporting function for the reset_attrs() method. It should be run with the rig in its default pose.

    Parameters
    ----------
    suffix : str
        Suffix to identify the desired nodes.

    Returns
    -------
    no return
    """
    all_nodes = cmds.ls(suffix)
    cmds.select(all_nodes, replace=True)

    all_ctrls_with_custom_attrs = []

    for node in all_nodes:
        custom_attrs = [attr for attr in cmds.listAttr(node) if attr.endswith("_attr") or attr.endswith("_attr_proxy")]
        for attr in custom_attrs:
            attr_value = cmds.getAttr("{0}.{1}".format(node, attr))
            all_ctrls_with_custom_attrs.append((node, attr, round(attr_value, 2)))
        
    print(all_ctrls_with_custom_attrs)

def reset_all_attrs(suffix="*_ctrl"):
    """Reset all nodes to their default values. For custom attributes the default values should be filled manually based on the output of the function print_all_custom_fields_default_values().

    Parameters
    ----------
    ctrl_suffix : str
        Suffix to identify nodes that are controls.

    Returns
    -------
    no return
    """
    all_nodes = cmds.ls(suffix)
    cmds.select(all_nodes, replace=True)
    
    all_custom_fields_default_values = [] # This list should be filled manually for each rig. The value should be the output of the function print_all_custom_fields_default_values()

    for node in all_nodes:
        __reset_ctrl(all_custom_fields_default_values, node)

def reset_ctrls():
    """Reset the selected controls to their default values. For custom attributes the default values should be filled manually based on the output of the function print_all_custom_fields_default_values().

    Parameters
    ----------
    control : selection
        Selected controls to reset.

    Returns
    -------
    no return
    """
    selection = cmds.ls(orderedSelection=True)

    if len(selection) < 1:
        raise Exception("Please select at least one control in order to reset.")
    
    all_custom_fields_default_values = [] # This list should be filled manually for each rig. The value should be the output of the function print_all_custom_fields_default_values().

    for node in selection:
        __reset_ctrl(all_custom_fields_default_values, node)

def reset_ctrl(ctrl):
    """Reset the input control to their default values. For custom attributes the default values should be filled manually based on the output of the function print_all_custom_fields_default_values().

    Parameters
    ----------
    ctrl : str
        Selected control to reset.

    Returns
    -------
    no return
    """

    all_custom_fields_default_values = [] # This list should be filled manually for each rig. The value should be the output of the function print_all_custom_fields_default_values().

    __reset_ctrl(all_custom_fields_default_values, ctrl)

def get_attrs_values(transform):
    """Returns a dict with all the current attributes values for the given transform.

    Parameters
    ----------
    transform : str
        A transform to get the attributes values

    Returns
    -------
        dict:
            Dictionary with all the default attributes values.
    """
    values = {}
    for attr in default_attrs:
        values[attr] = cmds.getAttr(name(transform, attr))
    return values

def __reset_ctrl(all_custom_fields_default_values, node):
    custom_attrs = [custom_fields for custom_fields in all_custom_fields_default_values if custom_fields[0] == node]
    for _, custom_attr_name, custom_attr_value in custom_attrs:
        if cmds.getAttr("{0}.{1}".format(node, custom_attr_name), settable=True):
            cmds.setAttr("{0}.{1}".format(node, custom_attr_name), custom_attr_value)
    for default_attr_name in default_attrs:
        if cmds.getAttr("{0}.{1}".format(node, default_attr_name), settable=True):
            cmds.setAttr("{0}.{1}".format(node, default_attr_name), 1 if default_attr_name.startswith("s") or default_attr_name.startswith("v") else 0)

def __get_channel_box_selected_attributes():
    
    channel_box = mel.eval( 'global string $gChannelBoxName; $temp=$gChannelBoxName;' )
    selected_attrs = cmds.channelBox(channel_box, query=True, selectedMainAttributes=True)
    
    return selected_attrs
    
def __validate_selection(selection):
    
    result = True
    
    if len(selection) != 2:
        result = False

    return result

def __create_attribute_enum(target_node, attr_type, long_name, nice_name, default_value, enum_values):
    cmds.select(target_node, replace=True)
    cmds.addAttr(longName = long_name, niceName = nice_name, attributeType = attr_type, keyable = True, defaultValue = default_value, enumName = enum_values)
    
    created_attr_name = name(target_node, long_name)
    
    return created_attr_name
    
def __create_attribute_numeric(target_node, attr_type, long_name, nice_name, max_value=None, min_value=None, soft_min=None, soft_max=None, default_value=None):
    cmds.select(target_node, replace=True)
    cmds.addAttr(longName = long_name, niceName = nice_name, attributeType = attr_type, keyable = True, defaultValue = default_value) 
    
    created_attr_name = name(target_node, long_name)
    
    if(max_value is not None):
        cmds.addAttr( created_attr_name, edit=True, maxValue=max_value )
    if(min_value is not None):
        cmds.addAttr( created_attr_name, edit=True, minValue=min_value )
    if(soft_max is not None):
        cmds.addAttr( created_attr_name, edit=True, softMaxValue=soft_max )
    if(soft_min is not None):
        cmds.addAttr( created_attr_name, edit=True, softMinValue=soft_min )
        
    return created_attr_name

def __set_attribute_access(attr_name, locked, keyable):
    cmds.setAttr( attr_name, lock=locked )
    cmds.setAttr( attr_name, channelBox=True )
    cmds.setAttr( attr_name, keyable=keyable )

def __valid_attribute(attr):
    
    _valid_attributes = ["enum", "float", "double", "integer"]
    
    if attr not in _valid_attributes:
        return False
            
    return True

def __copy_attribute(source_node, target_node, attr):
    
    created_attr_name = ""
    
    attr_type= cmds.attributeQuery( attr, node=source_node, attributeType=True )
    long_name = cmds.attributeQuery( attr, node=source_node, longName=True )
    nice_name = cmds.attributeQuery( attr, node=source_node, niceName=True )
    default_values = cmds.attributeQuery( attr, node=source_node, listDefault=True )
    locked = cmds.getAttr("{0}.{1}".format(source_node, attr), lock=True)
    keyable = cmds.getAttr("{0}.{1}".format(source_node, attr), keyable=True)
    
    if (attr_type == "enum"):
        
        enum_values = cmds.attributeQuery( attr, node=source_node, listEnum=True )[0]
        created_attr_name = __create_attribute_enum(target_node, attr_type = attr_type, long_name = long_name, nice_name = nice_name, enum_values = enum_values, default_value = default_values[0])
    
    elif attr_type in ["float", "double", "integer"]:
        
        max_value, min_value, soft_max, soft_min = __get_numeric_attributes(source_node, attr)
        created_attr_name = __create_attribute_numeric(target_node, attr_type = attr_type, long_name = long_name, nice_name = nice_name, max_value = max_value, min_value = min_value, soft_min = soft_min, soft_max = soft_max, default_value = default_values[0])
    
    __set_attribute_access(created_attr_name, locked, keyable)

def __get_numeric_attributes(source_node, attr):
    
    max_value = None
    min_value = None
    soft_max = None
    soft_min = None
        
    if(cmds.attributeQuery( attr, node=source_node, maxExists=True )):
        max_value = cmds.attributeQuery( attr, node=source_node, maximum=True )[0]
            
    if(cmds.attributeQuery( attr, node=source_node, minExists=True )):
       min_value = cmds.attributeQuery( attr, node=source_node, minimum=True )[0]
        
    if(cmds.attributeQuery( attr, node=source_node, softMinExists=True )):
       soft_min = cmds.attributeQuery( attr, node=source_node, softMin=True )[0]
           
    if(cmds.attributeQuery( attr, node=source_node, softMaxExists=True )):
       soft_max = cmds.attributeQuery( attr, node=source_node, softMax=True )[0]

    return max_value,min_value,soft_max,soft_min

def __is_copy_to_same_object(selection):
    
    result = False
    
    if len(selection) == 1:
        result = True
        
    return result

if __name__ == "__main__":
    copy_attrs_values("pCube1", "pSphere1")