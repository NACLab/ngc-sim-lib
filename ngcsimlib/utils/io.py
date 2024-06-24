import uuid, os, json


def make_unique_path(directory, root_name=None):
    """
    This block of code will make a uniquely named directory inside the specified output folder.
    If the root name already exists it will append a UID to the root name to not overwrite data

    Args:
        directory: The root directory to save models to

        root_name: (Default None) The root name for the model to be saved to,
            if none it will just use the UID

    Returns:
        path to created directory
    """
    uid = uuid.uuid4()
    if root_name is None:
        root_name = str(uid)
        print("generated path will be named \"" + str(root_name) + "\"")

    elif os.path.isdir(directory + "/" + root_name):
        root_name += "_" + str(uid)
        print("root path already exists, generated path will be named \"" + str(root_name) + "\"")

    path = directory + "/" + str(root_name)
    os.mkdir(path)
    return path


def check_serializable(dict):
    """
    Verifies that all the values of a dictionary are serializable

    Args:
        dict: dictionary to check

    Returns:
        list of all the keys that are not serializable
    """
    bad_keys = []
    for key in dict.keys():
        try:
            json.dumps(dict[key])
        except:
            bad_keys.append(key)
    return bad_keys
