class AvalaraException(Exception):
    pass


class AvalaraServerException(Exception):
    pass


class AvalaraBase(object):
    __fields__ = []
    __contains__ = []

    def __init__(self, *args, **kwargs):
        for field in self.__contains__:
            setattr(self, field, [])
        self.update(**kwargs)

    def update(self, *args, **kwargs):
        for k,v in kwargs.iteritems():
            if k in self.__fields__:
                setattr(self, k, v)
            elif k in self.__contains__:
                getattr(self, k).append(v)

    def tojson(self):
        data = {}
        for f in self.__fields__:
            data[f] = getattr(self, f)
        for f in self.__contains__:
            data[f] = []
            for obj in getattr(self, f):
                data[f].append(obj.tojson())
        return data

import api
