from avalara.base import Document, BaseResponse, BaseAPI, AvalaraException, AvalaraServerException, ErrorResponse


def except_500_and_return(fn):
    def newfn(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except AvalaraServerException as e:
            return ErrorResponse(e.response)
    return newfn


class API(BaseAPI):

    PRODUCTION_HOST = 'rest.avalara.net'
    DEVELOPMENT_HOST = 'development.avalara.net'
    VERSION = '1.0'
    company_code = None

    def __init__(self, account_number, license_key, company_code, live=False, **kwargs):
        self.company_code = company_code
        super(API, self).__init__(username=account_number, password=license_key, live=live, **kwargs)

    @except_500_and_return
    def get_tax(self, lat, lng, doc):
        try:
            stem = '/'.join([self.VERSION, 'tax', '%.6f,%.6f' % (lat, lng), 'get'])
        except TypeError:
            raise AvalaraException('Please pass lat and long as floats, or Decimal')
        data = {'saleamount': doc.total}
        resp = self._get(stem, data)
        return GetTaxResponse(resp)

    @except_500_and_return
    def post_tax(self, doc, commit=False):
        stem = '/'.join([self.VERSION, 'tax', 'get'])
        setattr(doc, 'CompanyCode', self.company_code)
        if commit:
            setattr(doc, 'Commit', True)
        data = doc.todict()
        resp = self._post(stem, data)
        tax_resp = PostTaxResponse(resp)
        if not hasattr(doc, 'DocCode'):
            doc.update_doc_code_from_response(tax_resp)
        return tax_resp

    @except_500_and_return
    def cancel_tax(self, doc, reason=None, doc_id=None):
        if reason and (not reason in Document.CANCEL_CODES):
            raise AvalaraException("Please pass a valid cancel code")
        stem = '/'.join([self.VERSION, 'tax', 'cancel'])
        data = {
            'CompanyCode': doc.CompanyCode,
            'DocType': doc.DocType,
        }
        if reason:
            data.update({'CancelCode': reason})
        if hasattr(doc, 'DocCode'):
            data.update({'DocCode': doc.DocCode})
        _doc_id = None
        if hasattr(doc, 'DocId'):
            _doc_id = doc.DocId
        if doc_id:
            _doc_id = doc_id
        if _doc_id:
            data.update({'DocId': _doc_id})
        resp = self._post(stem, data)
        return CancelTaxResponse(resp)

    @except_500_and_return
    def validate_address(self, address):
        stem = '/'.join([self.VERSION, 'address', 'validate'])
        resp = self._get(stem, address.todict())
        return AddressValidateResponse(resp)


class GetTaxResponse(BaseResponse):
    __fields__ = ['Rate', 'Tax']
    __contains__ = ['TaxDetails']


class PostTaxResponse(BaseResponse):
    __fields__ = ['DocCode', 'DocId', 'DocDate', 'Timestamp', 'TotalAmount', 'TotalDiscount', 'TotalExemption', 'TotalTaxable', 'TotalTax', 'TotalTaxCalculated', 'TaxDate']
    __contains__ = ['TaxLines', 'TaxDetails', 'TaxAddresses']


class CancelTaxResponse(BaseResponse):
    __has__ = ['CancelTaxResult']

    @property
    def is_success(self):
        return True if self.CancelTaxResult.ResultCode == BaseResponse.SUCCESS else False


class AddressValidateResponse(BaseResponse):
    __has__ = ['Address']
