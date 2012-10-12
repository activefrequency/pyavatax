from avalara import AvalaraBase, AvalaraException
try:
    from django.conf import settings
except ImportError:
    from avalara import settings


class BaseAPI(object):

    @staticmethod
    def _get(stem, data):
        return API._request('GET', stem, data)

    @staticmethod
    def _post(stem, data):
        return API._request('POST', stem, data)

    @staticmethod
    def _request(http_method, stem, data):
        url = '/'.join([API.url] + stem)

    @staticmethod
    def handle_response(response):
        return 


class BaseResponse(AvalaraBase):
    SUCCESS = 'Success'

    def __init__(self, response, *args, **kwargs):
        self.response = response
        super(BaseResponse, self).__init__(*args, **kwargs)

    def is_success(self):
        try:
            if self.response.has_key('ResultCode'):
                return True if self.response.get('ResultCode', False) == BaseResponse.SUCCESS else False
            else:
                raise AvalaraException('is_success not applicable for this response')
        except AttributeError:
            raise AvalaraException('No response found')


class API(BaseAPI):
    url = None

    def __init__(self, *args, **kwargs):
        self.url = settings.AVALARA_PRODUCTION_URL if settings.AVALARA_LIVE else settings.AVALARA_DEVELOPMENT_URL
    
    def ping(self):
        stem = 'ping'
        data = {}
        API._get(stem, data)

    def get_tax(self, document):
        stem = '/'.join(['tax','get'])
        data = {}
        API._get(stem, data)

    def post_tax(self, document):
        stem = '/'.join(['tax','get'])
        data = document.tojson()
        API._post(stem, data)

    def cancel_tax(self, document):
        stem = '/'.join(['tax','cancel'])
        data = {
            'CompanyCode': '',
            'DocType': '',
            'DocCode': '',
            'CancelCode': '',
        }
        API._post(stem, data)


class PingResponse(BaseResponse):
    pass


class GetTaxResponse(BaseResponse):
    pass


class PostTaxResponse(BaseResponse):
    __fields__ = ['DocCode', 'DocDate', 'Timestamp', 'TotalAmount', 'TotalDiscount', 'TotalExemption', 'TotalTaxable', 'TotalTax', 'TotalTaxCalculated', 'TaxDate']
    __contains__ = ['TaxLines', 'TaxDetails', 'TaxAddress']


class CancelTaxResponse(BaseResponse):
    __contains__ = ['CancelTaxResult']

    def is_success(self):
        try:
            return True if self.response.get('CancelTaxResult').get('ResultCode') == BaseResponse.SUCCESS else False
        except IndexError:
            raise AvalaraException('No response was found')


