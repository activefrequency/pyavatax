from avalara.base import Document, BaseResponse, BaseAPI, AvalaraException, AvalaraServerException, ErrorResponse
import decorator

@decorator.decorator
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

    def __init__(self, account_number, license_key, company_code, live=False, **kwargs):
        self.company_code = company_code
        super(API, self).__init__(username=account_number, password=license_key, live=live, **kwargs)

    @except_500_and_return
    def get_tax(self, lat, lng, doc):
        """Performs a HTTP GET to tax/get/"""
        try:
            stem = '/'.join([self.VERSION, 'tax', '%.6f,%.6f' % (lat, lng), 'get'])
        except TypeError:
            raise AvalaraException('Please pass lat and long as floats, or Decimal')
        data = {'saleamount': doc.total}
        resp = self._get(stem, data)
        return GetTaxResponse(resp)

    @except_500_and_return
    def post_tax(self, doc, commit=False):
        """Performs a HTTP POST to tax/get/"""
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
        """Performs a HTTP POST to tax/cancel/"""
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
        """Performs a HTTP GET to address/validate/"""
        stem = '/'.join([self.VERSION, 'address', 'validate'])
        resp = self._get(stem, address.todict())
        return ValidateAddressResponse(resp)


class GetTaxResponse(BaseResponse):
    __fields__ = ['Rate', 'Tax']
    __contains__ = ['TaxDetails']


class PostTaxResponse(BaseResponse):
    __fields__ = ['DocCode', 'DocId', 'DocDate', 'Timestamp', 'TotalAmount', 'TotalDiscount', 'TotalExemption', 'TotalTaxable', 'TotalTax', 'TotalTaxCalculated', 'TaxDate']
    __contains__ = ['TaxLines', 'TaxDetails', 'TaxAddresses']


class CancelTaxResponse(BaseResponse):
    __has__ = ['CancelTaxResult']

    # cancel tax just had to structure this differently didn't they
    @property
    def _details(self):
        try:
            return [{m.RefersTo: m.Summary} for m in self.CancelTaxResult.Messages]
        except AttributeError:  # doesn't have RefersTo
            return [{m.Source: m.Summary} for m in self.CancelTaxResult.Messages]

    @property
    def is_success(self):
        """Returns whether or not the response was successful.
        Avalara bungled this response, it is formatted differently than every other response"""
        try:
            return True if self.CancelTaxResult.ResultCode == BaseResponse.SUCCESS else False
        except AttributeError:
            raise AvalaraException('error not applicable for this response')

    @property
    def error(self):
        """Returns a list of tuples. The first position in the tuple is
        either the offending field that threw an error, or the class in
        the Avalara system that threw it. The second position is a
        human-readable message from Avalara.
        Avalara bungled this response, it is formatted differently than every other response"""
        cond = False
        try:
            cond = self.CancelTaxResult.ResultCode == BaseResponse.ERROR
        except AttributeError:
            raise AvalaraException('error not applicable for this response')
        return self._details if cond else False


class ValidateAddressResponse(BaseResponse):
    __has__ = ['Address']
