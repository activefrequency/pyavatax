import requests
from avalara import AvalaraException, AvalaraServerDetailException
from avalara.base import AvalaraBase, Document


class BaseAPI(object):

    headers = { 'Content-Type': 'text/json; charset=utf-8', }

    def _get(self, stem, data):
        return self._request('GET', stem, params=data)

    def _post(self, stem, data, params={}):
        return self._request('POST', stem, params=params, data=data)

    def _request(self, http_method, stem, data={}, params={}):
        url = '%s/%s' % (self.url, stem)
        resp = None
        kwargs = {
            'params': params,
            'data': data,
            'headers': self.headers,
            'auth': (self.username, self.password)
        }
        if http_method == 'GET':
            resp = requests.get(url, **kwargs)
        elif http_method == 'POST':
            resp = requests.post(url, **kwargs)
        if resp.status_code == requests.codes.ok:
            if resp.json is None:
                raise AvalaraServerDetailException(resp)
            return resp.json
        else:
            raise AvalaraServerDetailException(resp)


class BaseResponse(AvalaraBase):
    SUCCESS = 'Success'
    ERROR = 'Error'

    def __init__(self, response_as_json, *args, **kwargs):
        self.response = response_as_json
        super(BaseResponse, self).__init__(*args, **response_as_json)

    @property
    def is_success(self):
        try:
            if self.response.has_key('ResultCode'):
                return True if self.response.get('ResultCode', BaseResponse.ERROR) == BaseResponse.SUCCESS else False
            else:
                raise AvalaraException('is_success not applicable for this response')
        except AttributeError:
            raise AvalaraException('No response found')

    @property
    def error(self):
        if not self.response.has_key('ResultCode'):
            raise AvalaraException('is_error not applicable for this response')
        if self.response.get('ResultCode', BaseResponse.SUCCESS) == BaseResponse.ERROR:
            messages = []
            for message in self.response.get('Messages'):
                messages.append((message.get('RefersTo'), message.get('Summary')))
            raise AvalaraException(messages, self.response)
        else:
            raise AvalaraException('This is a successful response')


class API(BaseAPI):
    PRODUCTION_URL = 'https://rest.avalara.net'
    DEVELOPMENT_URL = 'https://development.avalara.net'
    VERSION = '1.0'
    url = None
    username = None
    password = None
    company_code = None

    def __init__(self, account_number, license_key, company_code, live=False, **kwargs):
        self.url = API.PRODUCTION_URL if live else API.DEVELOPMENT_URL
        self.username = account_number
        self.password = license_key
        self.company_code = company_code
    
    def get_tax(self, lat, lng, document):
        stem = '/'.join([self.VERSION, 'tax','%.6f,%.6f' % (lat, lng), 'get'])
        data = {
            'saleamount': document.total
        }
        resp = self._get(stem, data)
        return GetTaxResponse(resp)

    def post_tax_and_commit(self, document):
        setattr(document, 'Commit', True)
        self.post_tax(document)

    def post_tax(self, document):
        stem = '/'.join([self.VERSION, 'tax','get'])
        setattr(document, 'CompanyCode', self.company_code)
        data = document.tojson()
        resp = self._post(stem, data)
        return PostTaxResponse(resp)

    def cancel_tax_unspecified(self, document):
        self.cancel_tax(document, document.CANCEL_UNSPECIFIED)

    def cancel_tax_post_failed(self, document):
        self.cancel_tax(document, document.CANCEL_POST_FAILED)

    def cancel_tax_doc_deleted(self, document):
        self.cancel_tax(document, document.CANCEL_DOC_DELETED)

    def cancel_tax_doc_voided(self, document):
        self.cancel_tax(document, document.CANCEL_DOC_VOIDED)

    def cancel_tax_adjustment_canceled(self, document):
        self.cancel_tax(document, document.CANCEL_CODES)
    
    def cancel_tax(self, document, cancel_code):
        if not cancel_code in Document.CANCEL_CODES:
            raise AvalaraException("Please pass a valid cancel code")
        stem = '/'.join([self.VERSION, 'tax','cancel'])
        data = {
            'CompanyCode': document.CompanyCode,
            'DocType': document.DocType,
            'DocCode': document.DocCode,
            'CancelCode': cancel_code,
        }
        resp = self._post(stem, data)
        return CancelTaxResponse(resp)

    def address_validate(self, address):
        stem = '/'.join([self.VERSION, 'address', 'validate' ])
        resp = self._get(stem, address.tojson())
        return AddressValidateResponse(resp)


class GetTaxResponse(BaseResponse):
    __fields__ = ['Rate', 'Tax']
    __contains__ = ['TaxDetails']


class PostTaxResponse(BaseResponse):
    __fields__ = ['DocCode', 'DocDate', 'Timestamp', 'TotalAmount', 'TotalDiscount', 'TotalExemption', 'TotalTaxable', 'TotalTax', 'TotalTaxCalculated', 'TaxDate']
    __contains__ = ['TaxLines', 'TaxDetails', 'TaxAddress']


class CancelTaxResponse(BaseResponse):
    __has__ = ['CancelTaxResult']

    def is_success(self):
        try:
            return True if self.response.get('CancelTaxResult').get('ResultCode') == BaseResponse.SUCCESS else False
        except IndexError:
            raise AvalaraException('No response was found')


class AddressValidateResponse(BaseResponse):
    __has__ = ['Address']
