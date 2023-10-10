import maya.cmds as cmds

def set_driven_key(driver_attr, driven_attr, driver_value = 0, driven_value = 0):
    """Encapsulate the call to create set driven keys.

    Parameters
    ----------
    driver_attr : str
        The driver object name.
    driven_attr : str
        The driver object name.
    driver_value: float, optional
        Value on the driver object that will drive that value on the driven object.
    driven_value: float, optional
        Value on the driven object that will be triggered by a value on the driver object.
    
    Returns
    -------
        no return. 
    """
    cmds.setDrivenKeyframe(driven_attr, 
                        currentDriver = driver_attr,
                        value = driven_value,
                        driverValue = driver_value)