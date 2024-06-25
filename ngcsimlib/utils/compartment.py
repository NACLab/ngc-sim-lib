""" Note these are to get a copied hash table of values not the actual
compartments"""

__all_compartments = {}

def Get_Compartment_Batch(compartment_uids=None):
    """
    This method should be used sparingly

    Get a subset of all compartment values based on provided paths. If no paths are provided it will grab all of them

    Args:
        compartment_uids: needed ids

    Returns:
        a subset of all compartment values

    """
    if compartment_uids is None:
        return {key: c.value for key, c in __all_compartments.items()}
    return {key: __all_compartments[key].value for key in compartment_uids}


def Set_Compartment_Batch(compartment_map=None):
    """
    This method should be used sparingly

    Sets a subset of compartments to their corresponding value in the provided dictionary

    Args:
        compartment_map: a map of compartment paths to values
    """
    if compartment_map is None:
        return

    for key, value in compartment_map.items():
        if key not in __all_compartments.keys():
            __all_compartments[key] = value
        else:
            __all_compartments[key].set(value)


def get_compartment_by_name(context, name):
    """
    Gets a specific compartment from a given context

    Args:
        context: context to extract compartment from

        name: name of compartment to get

    Returns: expected compartment, None if not a valid compartment

    """
    return __all_compartments.get(context.path + "/" + name, None)

