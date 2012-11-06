import datetime
import logging
import json

import requests


def str_to_class(klassname):
    """Returns class of string parameter. Requires class to be in module namespace"""
    import sys
    import types
    try:
        identifier = getattr(sys.modules[__name__], klassname)
    except AttributeError:
        raise NameError("%s doesn't exist." % klassname)
    if isinstance(identifier, (types.ClassType, types.TypeType)):
        return identifier
    raise TypeError("%s is not a class." % klassname)


def isiterable(foo):
    try:
        iter(foo)
    except TypeError:
        return False
    else:
        return True


class AvalaraBase(object):
    """Base object for parsing and outputting json"""
    __fields__ = []  # a list of simple attributes on this object
    __contains__ = []  # a list of other objects contained by this object
    __has__ = []  # a list of single objects contained by this object

    def __init__(self, *args, **kwargs):
        self.__setup__()
        self.update(**kwargs)

    def __setup__(self):
        """Initiate lists for objects contained within this object"""
        for field in self.__contains__:
            setattr(self, field, [])

    def clean(self):
        if hasattr(self, '__testing_ignore_validate__'):
            return  # passthrough for a test
        """Validate fields"""
        for f in self.__fields__:
            clean_fn = 'clean_%s' % f
            if hasattr(self, clean_fn):
                getattr(self, clean_fn)()
        for f in self.__has__:
            if hasattr(self, f):
                getattr(self, f).clean()
        for f in self.__contains__:
            for v in getattr(self, f):
                v.clean()

    def _handle_pluralize(self, k):
        _k = 'Address' if k == 'Addresses' else k
        _k = 'Line' if k == 'Lines' else _k
        return _k

    def update(self, *args, **kwargs):
        """Updates kwargs onto attributes of self"""
        for k, v in kwargs.iteritems():
            if k in self.__fields__:
                setattr(self, k, v)
            elif k in self.__has__:  # has an object
                klass = str_to_class(self._handle_pluralize(k))
                if isinstance(v, klass):
                    setattr(self, k, v)
                elif isinstance(v, dict):
                    setattr(self, k, klass(**v))
            elif k in self.__contains__:  # contains many objects
                klass = str_to_class(self._handle_pluralize(k))
                for _v in v:
                    if isinstance(_v, klass):
                        getattr(self, k).append(_v)
                    elif isinstance(_v, dict):
                        getattr(self, k).append(klass(**_v))
            else:
                raise AvalaraException('%s is not a valid field' % k)
        self.clean()

    def todict(self):
        """Returns a dict of attributes on object"""
        if hasattr(self, 'validate') and not hasattr('self', '__testing_ignore_validate__'):
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
    """Handles HTTP and requests library"""

    default_headers = {'Content-Type': 'text/json; charset=utf-8'}
    PRODUCTION_HOST = None
    DEVELOPMENT_HOST = None
    protocol = 'https'
    default_timeout = 10.0
    logger = None

    def __init__(self, username=None, password=None, live=False, timeout=None, proxies={}, **kwargs):
        self.host = self.PRODUCTION_HOST if live else self.DEVELOPMENT_HOST  # from the child API class
        self.url = "%s://%s" % (BaseAPI.protocol, self.host)
        self.username = username
        self.proxies = proxies
        self.headers = BaseAPI.default_headers.update({'Host': self.host})
        self.password = password
        self.timeout = timeout or BaseAPI.default_timeout
        BaseAPI.logger = logging.getLogger('pyavatax.api')

    def _get(self, stem, data):
        return self._request('GET', stem, params=data)

    def _post(self, stem, data, params={}):
        return self._request('POST', stem, params=params, data=data)

    def _request(self, http_method, stem, data={}, params={}):
        url = '%s/%s' % (self.url, stem)
        kwargs = {
            'params': params,
            'data': json.dumps(data),
            'headers': self.headers,
            'auth': (self.username, self.password),
            'proxies': self.proxies,
            'timeout': self.timeout
        }
        resp = None
        try:
            if http_method == 'GET':
                resp = requests.get(url, **kwargs)
            elif http_method == 'POST':
                resp = requests.post(url, **kwargs)
        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError, requests.exceptions.Timeout) as e:
            BaseAPI.logger.error(e)
            raise AvalaraServerNotReachableException(e)
        if resp.status_code == requests.codes.ok:
            if resp.json is None:
                raise AvalaraServerDetailException(resp)
            return resp
        else:
            raise AvalaraServerDetailException(resp)


class BaseResponse(AvalaraBase):
    """Common functionality for handling Avalara server responses"""
    SUCCESS = 'Success'
    ERROR = 'Error'
    __fields__ = ['ResultCode']
    __contains__ = ['Messages']

    def __init__(self, response, *args, **kwargs):
        self.response = response
        super(BaseResponse, self).__init__(*args, **response.json)

    @property
    def _details(self):
        try:
            return [{m.RefersTo: m.Summary} for m in self.Messages]
        except AttributeError:  # doesn't have RefersTo
            return [{m.Source: m.Summary} for m in self.Messages]

    @property
    def is_success(self):
        """Returns whether or not the response was successful"""
        if not hasattr(self.response, 'json'):
            raise AvalaraException('No response found')
        if 'ResultCode' not in self.response.json:
            raise AvalaraException('is_success not applicable for this response')
        cond = self.response.json.get('ResultCode', BaseResponse.ERROR) == BaseResponse.SUCCESS
        return True if cond else False

    @property
    def error(self):
        """Returns a list of tuples. The first position in the tuple is
        either the offending field that threw an error, or the class in
        the Avalara system that threw it. The second position is a
        human-readable message from Avalara"""
        if 'ResultCode' not in self.response.json:
            raise AvalaraException('error not applicable for this response')
        cond = self.response.json.get('ResultCode', BaseResponse.SUCCESS) == BaseResponse.ERROR
        return self._details if cond else False


class ErrorResponse(BaseResponse):
    """Common error case functionality from a 500 error"""
    __fields__ = ['ResultCode']
    __contains__ = ['Messages']

    @property
    def is_success(self):
        """Returns whether or not the response was successful"""
        return False  # this is always a 500 error

    @property
    def error(self):
        """Returns a list of tuples. The first position in the tuple is
        either the offending field that threw an error, or the class in
        the Avalara system that threw it. The second position is a
        human-readable message from Avalara"""
        return self._details


class AvalaraBaseException(Exception):
    """Common base for all our exceptions"""
    pass


class AvalaraException(AvalaraBaseException):
    """Raised when operating unsuccessfully with document, address, line, etc objects"""
    pass


class AvalaraServerNotReachableException(AvalaraBaseException):
    """Raised when the AvaTax service is unreachable for any reason and no response is received"""
    
    def __init__(self, request_exception, *args, **kwargs):
        self.request_exception = request_exception

    def __str__(self):
        return repr(self.request_exception)


class AvalaraServerException(AvalaraBaseException):
    """Used internally to handle 500 and other server error responses"""

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
        """Returns all the info we have about the request and response"""
        fmt = "Status: %r \n Method: %r, \n URL: %r \n Data: %r \n Errors: %r "
        return fmt % (repr(self.status_code), repr(self.method), repr(self.url), repr(self.request_data), repr(self.errors))

    @property
    def errors(self):
        """Will return an ErrorResponse details property, or the raw text server response"""
        return ErrorResponse(self.response)._details if self.has_details else self.raw_response

    def __str__(self):
        return "%r, %r %r" % (repr(self.status_code), repr(self.method), repr(self.url))


class AvalaraServerDetailException(AvalaraServerException):
    """Useful for seeing more detail through the tester and logs
    We always throw this exception, though you may catch
    AvalaraServerException if you don't care to see the details in the __str__"""

    def __str__(self):
        return self.full_request_as_string


class Document(AvalaraBase):
    """Represents the Avalara Document"""
    DOC_TYPE_SALE_ORDER = 'SalesOrder'
    DOC_TYPE_SALE_INVOICE = 'SalesInvoice'
    DOC_TYPE_RETURN_ORDER = 'ReturnOrder'
    DOC_TYPE_RETURN_INVOICE = 'ReturnInvoice'
    DOC_TYPE_PURCHASE_ORDER = 'PurchaseOrder'
    DOC_TYPE_PURCHASE_INVOICE = 'PurchaseInvoice'
    DOC_TYPE_INVENTORY_ORDER = 'InventoryTransferOrder'
    DOC_TYPE_INVENTORY_INVOICE = 'InventoryTransferInvoice'
    DOC_TYPES = (DOC_TYPE_SALE_ORDER, DOC_TYPE_SALE_INVOICE, DOC_TYPE_RETURN_ORDER, DOC_TYPE_RETURN_INVOICE, DOC_TYPE_PURCHASE_ORDER, DOC_TYPE_PURCHASE_INVOICE, DOC_TYPE_INVENTORY_ORDER, DOC_TYPE_INVENTORY_INVOICE)
    CANCEL_POST_FAILED = 'PostFailed'
    CANCEL_DOC_DELETED = 'DocDeleted'
    CANCEL_DOC_VOIDED = 'DocVoided'
    CANCEL_ADJUSTMENT_CANCELED = 'AdjustmentCanceled'
    CANCEL_CODES = (CANCEL_POST_FAILED, CANCEL_DOC_DELETED, CANCEL_DOC_VOIDED, CANCEL_ADJUSTMENT_CANCELED)

    logger = None

    __fields__ = ['DocType', 'DocId', 'DocCode', 'DocDate', 'CompanyCode', 'CustomerCode', 'Discount', 'Commit', 'CustomerUsageType', 'PurchaseOrderNo', 'ExemptionNo', 'PaymentDate', 'ReferenceCode']
    __contains__ = ['Lines', 'Addresses']  # the automatic parsing in `def update` doesn't work here, but its never invoked here
    __has__ = ['DetailLevel']

    def __init__(self, *args, **kwargs):
        super(Document, self).__init__(*args, **kwargs)
        Document.logger = logging.getLogger('pyavatax.api')

    @staticmethod
    def from_data(data):
        return Document(**data)

    @staticmethod
    def new_sales_order(*args, **kwargs):
        kwargs.update({'DocType': Document.DOC_TYPE_SALE_ORDER})
        return Document(*args, **kwargs)

    @staticmethod
    def new_sales_invoice(*args, **kwargs):
        kwargs.update({'DocType': Document.DOC_TYPE_SALE_INVOICE})
        return Document(*args, **kwargs)

    @staticmethod
    def new_return_order(*args, **kwargs):
        kwargs.update({'DocType': Document.DOC_TYPE_RETURN_ORDER})
        return Document(*args, **kwargs)

    @staticmethod
    def new_return_invoice(*args, **kwargs):
        kwargs.update({'DocType': Document.DOC_TYPE_RETURN_INVOICE})
        return Document(*args, **kwargs)

    @staticmethod
    def new_purchase_order(*args, **kwargs):
        kwargs.update({'DocType': Document.DOC_TYPE_PURCHASE_ORDER})
        return Document(*args, **kwargs)

    @staticmethod
    def new_purchase_invoice(*args, **kwargs):
        kwargs.update({'DocType': Document.DOC_TYPE_PURCHASE_INVOICE})
        return Document(*args, **kwargs)

    @staticmethod
    def new_inventory_order(*args, **kwargs):
        kwargs.update({'DocType': Document.DOC_TYPE_INVENTORY_ORDER})
        return Document(*args, **kwargs)

    @staticmethod
    def new_inventory_invoice(*args, **kwargs):
        kwargs.update({'DocType': Document.DOC_TYPE_INVENTORY_INVOICE})
        return Document(*args, **kwargs)

    def clean_DocType(self):
        doc_type = getattr(self, 'DocType', None)
        if doc_type and doc_type not in Document.DOC_TYPES:
            raise AvalaraException('%s is not a valid DocType' % doc_type)

    @staticmethod
    def _clean_float(f):
        if f and not isinstance(f, float):
            return float(f)
        elif f is None:
            return 0
        else:
            return f

    @staticmethod
    def _clean_int(i):
        if i and not isinstance(i, int):
            return int(i)
        elif i is None:
            return 0
        else:
            return i

    @staticmethod
    def _clean_date(date):
        if date and not isinstance(date, datetime.date):
            return datetime.datetime.strptime(date, '%Y-%m-%d').date()
        else:
            return date

    def clean_DocDate(self):
        doc_date = getattr(self, 'DocDate', None)
        try:
            date = Document._clean_date(doc_date)
            setattr(self, 'DocDate', date)
        except ValueError as e:
            raise AvalaraException('DocDate should either be a date object, or a string in this date format: YYYY-MM-DD')

    def clean_Discount(self):
        discount = getattr(self, 'Discount', None)
        try:
            f = Document._clean_float(discount)
            setattr(self, 'Discount', f)
        except ValueError:
            raise AvalaraException('Discount should either be a float, or string that is parsable into a float')

    def clean_Commit(self):
        commit = getattr(self, 'Commit', None)
        if commit is not None:
            if commit is not True and commit is not False:
                raise AvalaraException('Commit should either be True, or False')

    def clean_PaymentDate(self):
        pay_date = getattr(self, 'PaymentDate', None)
        try:
            date = Document._clean_date(pay_date)
            setattr(self, 'PaymentDate', date)
        except ValueError:
            raise AvalaraException('PaymentDate should either be a date object, or a string in this date format: YYYY-MM-DD')

    def set_detail_level(self, detail_level):
        """Add a DetailLevel instance to this Avalara document"""
        if isinstance(detail_level, DetailLevel):
            setattr(self, 'DetailLevel', detail_level)
        else:
            raise AvalaraException('%r is not a %r' % (detail_level, DetailLevel))

    def add_line(self, line):
        """Adds a Line instance to this document. Will provide a LineNo if you do not"""
        if not isinstance(line, Line):
            raise AvalaraException('%r is not a %r' % (line, Line))
        if not hasattr(line, 'LineNo'):
            count = len(self.Lines)
            setattr(line, 'LineNo', count + 1)  # start at one
            Document.logger.debug('%s inserting LineNo %d' % (getattr(self, 'DocCode', None), line.LineNo))
        self.Lines.append(line)

    def add_from_address(self, address):
        """Only use this function when performing a simple shipping operation. The default from address code will be used for this address"""
        if hasattr(self, 'from_address_code'):
            raise AvalaraException('You have already set a from address. If you are doing something beyond a simple order, just use the `add_address` method')
        if not isinstance(address, Address):
            raise AvalaraException('%r is not a %r' % (address, Address))
        if not hasattr(address, 'AddressCode'):
            setattr(address, 'AddressCode', Address.DEFAULT_FROM_ADDRESS_CODE)
            Document.logger.debug('%s setting default from address code' % getattr(self, 'DocCode', None))
        self.from_address_code = getattr(address, 'AddressCode')
        self.Addresses.append(address)

    def add_to_address(self, address):
        """Only use this function when performing a simple shipping operation. The default to address code will be used for this address"""
        if hasattr(self, 'to_address_code'):
            raise AvalaraException('You have already set a to address. If you are doing something beyond a simple order, just use the `add_address` method')
        if not isinstance(address, Address):
            raise AvalaraException('%r is not a %r' % (address, Address))
        if not hasattr(address, 'AddressCode'):
            setattr(address, 'AddressCode', Address.DEFAULT_TO_ADDRESS_CODE)
            Document.logger.debug('%s setting default to address code' % getattr(self, 'DocCode', None))
        self.to_address_code = getattr(address, 'AddressCode')
        self.Addresses.append(address)

    def add_address(self, address):
        """Adds an Address instance to this document. Nothing about the address will be changed, you are entirely responsible for it"""
        if not isinstance(address, Address):
            raise AvalaraException('%r is not a %r' % (address, Address))
        self.Address.append(address)

    def validate_codes(self):
        """Look through line items making sure that origin and destination codes are set
            set defaults if they exist, raise exception if we are missing something"""
        for l in self.Lines:
            if not hasattr(l, 'OriginCode'):
                if not hasattr(self, 'from_address_code'):
                    raise AvalaraException('Origin Code needed for Line Item %r' % l.LineNo)
                l.OriginCode = self.from_address_code
                Document.logger.debug('%s setting origin code %s' % (getattr(self, 'DocCode', None), l.OriginCode))
            if not hasattr(l, 'DestinationCode'):
                if not hasattr(self, 'to_address_code'):
                    raise AvalaraException('DestinationCode needed for Line Item %r' % l.LineNo)
                l.DestinationCode = self.to_address_code
                Document.logger.debug('%s setting destination code %s' % (getattr(self, 'DocCode', None), l.DestinationCode))

    def validate(self):
        """Ensures we have addresses and line items. Then calls validate_codes"""
        if not hasattr(self, 'DocType'):
            raise AvalaraException('You need to set a DocType')
        if len(self.Addresses) == 0:
            raise AvalaraException('You need Addresses')
        if len(self.Lines) == 0:
            raise AvalaraException('You need Line Items')
        self.validate_codes()

    @property
    def total(self):
        """Helper representing the line items total amount for tax. Used in GetTax call"""
        return sum([getattr(line, 'Amount', 0) for line in self.Lines])

    def update_doc_code_from_response(self, post_tax_response):
        """Sets the DocCode on the Document based on the response if Document does not have a DocCode"""
        from pyavatax.api import PostTaxResponse
        if not isinstance(post_tax_response, PostTaxResponse):
            raise AvalaraException('post_tax_response must be a %r' % type(PostTaxResponse))
        setattr(self, 'DocCode', getattr(post_tax_response, 'DocCode'))
        Document.logger.debug('AvaTax assigned %s as DocCode' % getattr(self, 'DocCode', None))


class Line(AvalaraBase):
    """Represents an Avalara Line"""
    __fields__ = ['LineNo', 'DestinationCode', 'OriginCode', 'Qty', 'Amount', 'ItemCode', 'TaxCode', 'CustomerUsageType', 'Description', 'Discounted', 'TaxIncluded', 'Ref1', 'Ref2']

    def __init__(self, *args, **kwargs):
        if 'Qty' not in kwargs:
            kwargs.update({'Qty': 1})
        return super(Line, self).__init__(*args, **kwargs)

    @staticmethod
    def from_data(data):
        return Line(**data)

    def clean_Qty(self):
        qty = getattr(self, 'Qty', None)
        try:
            i = Document._clean_int(qty)
            setattr(self, 'Qty', i)
        except ValueError:
            raise AvalaraException('Qty should either be a float, or string that is parsable into a float')

    def clean_Amount(self):
        amount = getattr(self, 'Amount', None)
        try:
            f = Document._clean_float(amount)
            setattr(self, 'Amount', f)
        except ValueError:
            raise AvalaraException('Amount should either be a float, or string that is parsable into a float')

    def clean_Discounted(self):
        discounted = getattr(self, 'Discounted', None)
        try:
            f = Document._clean_float(discounted)
            setattr(self, 'Discounted', f)
        except ValueError:
            raise AvalaraException('Discounted should either be a float, or string that is parsable into a float')

    def clean_TaxIncluded(self):
        tax = getattr(self, 'TaxIncluded', None)
        try:
            f = Document._clean_float(tax)
            setattr(self, 'TaxIncluded', f)
        except ValueError:
            raise AvalaraException('TaxIncluded should either be a float, or string that is parsable into a float')


class Address(AvalaraBase):
    """Represents an Avalara Address"""
    DEFAULT_FROM_ADDRESS_CODE = "1"
    DEFAULT_TO_ADDRESS_CODE = "2"
    __fields__ = ['AddressCode', 'Line1', 'Line2', 'Line3', 'PostalCode', 'Region', 'City', 'TaxRegionId', 'Country', 'AddressType', 'County', 'FipsCode', 'CarrierRoute', 'TaxRegionId', 'PostNet']

    @staticmethod
    def from_data(data):
        return Address(**data)

    @property
    def describe_address_type(self):
        """Returns human-readable description"""
        return {
            'F': "Firm or company address",
            'G': "General Delivery address",
            'H': "High-rise or business complex",
            'P': "PO Box address",
            'R': "Rural route address",
            'S': "Street or residential address",
            'NA': "No Address Type"
        }.get(getattr(self, 'AddressType'), 'NA')

    @property
    def describe_fips_code(self):
        """Returns human-readable description"""
        fips = len(getattr(self, 'FipsCode', ''))
        if fips == 0:
            return 'No FipsCode'
        elif fips >= 1 and fips <= 2:
            return 'State code'
        elif fips >= 3 and fips <= 5:
            return 'County code'
        elif fips >= 6 and fips <= 10:
            return 'City code'
        else:
            return 'Unknown'

    @property
    def describe_carrier_route(self):
        """Returns human-readable description"""
        return {
            'B': "PO Box",
            'C': "City delivery",
            'G': "General celivery",
            'H': "Highway contract",
            'R': "Rural route",
            'NA': 'No Carrier Route'
        }.get(getattr(self, 'CarrierRoute', 'NA'))

    @property
    def describe_post_net(self):
        """Returns human-readable description"""
        post = len(getattr(self, 'PostNet', ''))
        if post == 0:
            return 'No PostNet'
        elif post >= 1 and post <= 5:
            return 'Zip code'
        elif post >= 6 and post <= 9:
            return 'Plus4 code'
        elif post >= 10 and post >= 11:
            return 'Delivery point'
        elif post == 12:
            return 'Check digit'
        else:
            return 'Unknown'


class Messages(AvalaraBase):
    """Represents error messages dictionary response from Avalara"""
    __fields__ = ['Summary', 'RefersTo', 'Source', 'Details', 'Severity']


class DetailLevel(AvalaraBase):
    """Represents Avalara Detail Level request"""
    __fields__ = ['Line', 'Summary', 'Document', 'Tax', 'Diagnostic']


class TaxAddresses(AvalaraBase):
    """Represents TaxAddress response from Avalara"""
    __fields__ = ['Address', 'AddressCode', 'Latitude', 'Longitude', 'City', 'Country', 'PostalCode', 'Region', 'TaxRegionId', 'JurisCode']
    __contains__ = ['TaxDetails']


class TaxDetails(AvalaraBase):
    """Represents TaxDetails response from Avalara"""
    __fields__ = ['Country', 'Region', 'JurisType', 'Taxable', 'Rate', 'Tax', 'JurisName', 'TaxName']


class TaxLines(AvalaraBase):
    """Represents TaxLines response from Avalara"""
    __fields__ = ['LineNo', 'TaxCode', 'Taxability', 'Taxable', 'Rate', 'Tax', 'Discount', 'TaxCalculated', 'Exemption']
    __contains__ = ['TaxDetails']


class CancelTaxResult(AvalaraBase):
    """Represents CancelTaxResult response from Avalara"""
    __fields__ = ['DocId', 'TransactionId', 'ResultCode']
    __contains__ = ['Messages']
