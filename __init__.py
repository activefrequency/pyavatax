import datetime
import requests
import json


def isiterable(foo):
    try:
        iter(foo)
    except TypeError:
        return False
    else:
        return True


class AvalaraBase(object):
    __fields__ = []
    __contains__ = []
    __has__ = []

    def __init__(self, *args, **kwargs):
        self.__setup__()
        self.update(**kwargs)

    def __setup__(self):
        for field in self.__contains__:
            setattr(self, field, [])

    def update(self, *args, **kwargs):
        from avalara.base import str_to_class
        for k,v in kwargs.iteritems():
            if k in self.__fields__:
                setattr(self, k, v)
            elif k in self.__has__: # has an object
                klass = str_to_class(k)
                if isinstance(v, klass): 
                    setattr(self, k, v)
                elif type(v) == type({}): 
                    setattr(self, k, klass(**v))
            elif k in self.__contains__: # contains many objects
                klass = str_to_class(k)
                for _v in v:
                    if isinstance(_v, klass): 
                        getattr(self, k).append(_v)
                    elif type(_v) == type({}): 
                        getattr(self, k).append(klass(**_v))
                    
    def todict(self):
        if hasattr(self, 'validate'):
            self.validate()
        data = {}
        for f in self.__fields__:
            if hasattr(self, f):
                v = getattr(self, f)
                if isinstance(v, datetime.date) or isinstance(v, datetime.datetime):
                    v = v.isoformat()
                data[f] = v
        for f in self.__has__:
            if hasattr(self, f):
                obj = getattr(self, f)
                data[f] = obj.todict()
        for f in self.__contains__:
            if isiterable(getattr(self, f)):
                data[f] = []
                for obj in getattr(self, f):
                    data[f].append(obj.todict())
            else:
                data[f] = obj.todict()
        return data


class BaseAPI(object):

    headers = { 'Content-Type': 'text/json; charset=utf-8', }
    # useful for testing output with charlesproxy if you're getting a less-than-helpful error respose
    # if you suspect that headers are causing a problem with your requests, use this proxy,
    # the requests library doesn't control all the headers, libraries beneath it create more
    proxies = {
        # 'https': 'localhost:8888' 
    }
    PRODUCTION_HOST = None
    DEVELOPMENT_HOST = None 
    url = None
    host = None
    username = None
    password = None
    protocol = 'https'

    def __init__(self, username=None, password=None, live=False, **kwargs):
        self.host = self.PRODUCTION_HOST if live else self.DEVELOPMENT_HOST
        self.url = "%s://%s" % (self.protocol, self.host)
        self.username = username 
        self.headers.update({ 'Host': self.host }) 
        self.password = password 

    def _get(self, stem, data):
        return self._request('GET', stem, params=data)

    def _post(self, stem, data, params={}):
        return self._request('POST', stem, params=params, data=data)

    def _request(self, http_method, stem, data={}, params={}):
        url = '%s/%s' % (self.url, stem)
        resp = None
        kwargs = {
            'params': params,
            'data': json.dumps(data),
            'headers': self.headers,
            'auth': (self.username, self.password),
            'proxies': self.proxies
        }
        if http_method == 'GET':
            resp = requests.get(url, **kwargs)
        elif http_method == 'POST':
            resp = requests.post(url, **kwargs)
        if resp.status_code == requests.codes.ok:
            if resp.json is None:
                raise AvalaraServerDetailException(resp)
            return resp
        else:
            raise AvalaraServerDetailException(resp)


class BaseResponse(AvalaraBase):
    SUCCESS = 'Success'
    ERROR = 'Error'
    __fields__ = ['ResultCode']
    __contains__ = ['Messages']

    def __init__(self, response, *args, **kwargs):
        self.response = response
        super(BaseResponse, self).__init__(*args, **response.json)

    @property
    def details(self):
        return [ { m.RefersTo: m.Summary } for m in self.Messages ]

    @property
    def is_success(self):
        try:
            if self.response.json.has_key('ResultCode'):
                return True if self.response.json.get('ResultCode', BaseResponse.ERROR) == BaseResponse.SUCCESS else False
            else:
                raise AvalaraException('is_success not applicable for this response')
        except AttributeError:
            raise AvalaraException('No response found')

    @property
    def error(self):
        if not self.response.json.has_key('ResultCode'):
            raise AvalaraException('error not applicable for this response')
        if self.response.json.get('ResultCode', BaseResponse.SUCCESS) == BaseResponse.ERROR:
            return self.details
        else:
            return False


class ErrorResponse(BaseResponse): # represents a 500 Server error
    __fields__ = ['ResultCode']
    __contains__ = ['Messages']

    @property
    def is_success(self):
        return False # this is always a 500 error

    @property
    def error(self):
        return self.details


class AvalaraBaseException(Exception):
    pass


class AvalaraException(AvalaraBaseException):
    pass


class AvalaraServerException(AvalaraBaseException): # raised by a 500 response

    def __init__(self, response, *args, **kwargs):
        self.response = response
        self.status_code = response.status_code
        self.raw_response = response.text
        self.request_data = response.request.data
        self.method = response.request.method
        self.url = response.request.full_url
        self.has_details = True if response.json else False

    @property
    def full_request_as_string(self):
        return "Status: %r \n Method: %r, \n URL: %r \n Data: %r \n Errors: %r " % (repr(self.status_code), repr(self.method), repr(self.url), repr(self.request_data), repr(self.errors))

    @property
    def errors(self):
        if self.has_details:
            return ErrorResponse(self.response).details
        else:
            return self.raw_response

    def __str__(self):
        return "%r, %r" % (repr(self.status_code), repr(self.url))


# useful for seeing more detail through the tester and logs
# we always throw this exception, though you may catch
# AvalaraServerException if you don't care to see the details
class AvalaraServerDetailException(AvalaraServerException):

    def __str__(self):
        return self.full_request_as_string
