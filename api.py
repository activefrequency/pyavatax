from avalara import BaseResponse, BaseAPI, AvalaraException, AvalaraServerException, ErrorResponse
from avalara.base import Document


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
    def get_tax(self, lat, lng, document):
        stem = '/'.join([self.VERSION, 'tax','%.6f,%.6f' % (lat, lng), 'get'])
        data = {
            'saleamount': document.total
        }
        resp = self._get(stem, data)
        return GetTaxResponse(resp)

    def post_tax_and_commit(self, document):
        setattr(document, 'Commit', True)
        return self.post_tax(document)

    @except_500_and_return
    def post_tax(self, document):
        stem = '/'.join([self.VERSION, 'tax','get'])
        setattr(document, 'CompanyCode', self.company_code)
        data = document.todict()
        resp = self._post(stem, data)
        tax_resp = PostTaxResponse(resp)
        if not hasattr(document, 'DocCode'):
            document.update_doc_code_from_response(tax_resp)
        return tax_resp

    def cancel_tax_unspecified(self, document):
        return self.cancel_tax(document)

    def cancel_tax_post_failed(self, document):
        return self.cancel_tax(document, cancel_code=document.CANCEL_POST_FAILED)

    def cancel_tax_doc_deleted(self, document):
        return self.cancel_tax(document, cancel_code=document.CANCEL_DOC_DELETED)

    def cancel_tax_doc_voided(self, document):
        return self.cancel_tax(document, cancel_code=document.CANCEL_DOC_VOIDED)

    def cancel_tax_adjustment_canceled(self, document):
        return self.cancel_tax(document, cancel_code=document.CANCEL_CODES)
    
    @except_500_and_return
    def cancel_tax(self, document, cancel_code=None, doc_id=None):
        if cancel_code and (not cancel_code in Document.CANCEL_CODES):
            raise AvalaraException("Please pass a valid cancel code")
        stem = '/'.join([self.VERSION, 'tax','cancel'])
        data = {
            'CompanyCode': document.CompanyCode,
            'DocType': document.DocType,
        }
        if cancel_code:
            data.update({'CancelCode': cancel_code})
        if hasattr(document, 'DocCode'):
            data.update({ 'DocCode': document.DocCode })
        _doc_id = None
        if hasattr(document, 'DocId'):
            _doc_id = document.DocId
        if doc_id:
            _doc_id = doc_id
        if _doc_id:
            data.update({'DocId': _doc_id})
        resp = self._post(stem, data)
        return CancelTaxResponse(resp)

    @except_500_and_return
    def address_validate(self, address):
        stem = '/'.join([self.VERSION, 'address', 'validate' ])
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
