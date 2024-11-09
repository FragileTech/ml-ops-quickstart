def compute(args):
    """Compute a placeholder for the compute function.

    Example:
        >>> compute(["1", "2", "3"])
        '1'

    """
    return max(args, key=len)
