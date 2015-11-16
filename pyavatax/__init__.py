VERSION = (1, 3, 3)


from .api import API
from .base import Document, Address, Line


__all__ = ['API', 'Document', 'Address', 'Line', 'get_version']


def get_version():
    return ".".join([str(v) for v in VERSION])
