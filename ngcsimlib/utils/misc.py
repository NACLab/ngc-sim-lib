def extract_args(keywords=None, *args, **kwargs):
    """
    Extracts the given keywords from the provided args and kwargs. This method first finds all the matching keywords
    then for each missing keyword it takes the next value in args and assigns it. It will throw and error if there are
    not enough kwargs and args to satisfy all provided keywords

    Args:
        keywords: a list of keywords to extract

        args: the positional arguments to use as a fallback over keyword arguments

        kwargs: the keyword arguments to first try to extract from

    Returns:
        a dictionary for where each keyword is a key, and the value is assigned
            argument. Will throw a RuntimeError if it fails to match and argument
            to each keyword.
    """
    if keywords is None:
        return None

    a = {key: None for key in keywords}
    missing = []
    for key in keywords:
        if key in kwargs.keys():
            a[key] = kwargs.get(key, None)
        else:
            missing.append(key)

    if len(missing) > len(args):
        raise RuntimeError("Missing arguments")

    else:
        for idx, key in enumerate(missing):
            a[key] = args[idx]

    return a
