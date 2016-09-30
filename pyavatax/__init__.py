VERSION = (1, 3, 7)


def get_version():
    return ".".join([str(v) for v in VERSION])


__version__ = get_version()
__all__ = ['get_version', '__version__']
