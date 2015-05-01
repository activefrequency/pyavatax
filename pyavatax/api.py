import decorator
from pyavatax.base import Document, Address, BaseResponse, BaseAPI, AvalaraException, AvalaraTypeException, AvalaraValidationException, AvalaraServerException, ErrorResponse


@decorator.decorator
def except_500_and_return(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except AvalaraServerException as e:
        self = args[0]  # the first arg is self
        self.logger.error(e.full_request_as_string)
        resp = ErrorResponse(e.response)
        for arg in args:
            if isinstance(arg, Document):
                self.recorder.failure(arg, resp)
                break
        return resp


class API(BaseAPI):

    PRODUCTION_HOST = 'rest.avalara.net'
    DEVELOPMENT_HOST = 'development.avalara.net'
    VERSION = '1.0'

    def __init__(self, account_number, license_key, company_code, live=False, logger=None, recorder=None, **kwargs):
        """Constructor for API object. Also takes two optional kwargs: timeout, and proxies"""
        self.company_code = company_code
        super(API, self).__init__(username=account_number, password=license_key, live=live, logger=logger, recorder=recorder, **kwargs)

    @except_500_and_return
    def get_tax(self, lat, lng, doc, sale_amount=None):
        """Performs a HTTP GET to tax/get/"""
        if doc is not None:
            if isinstance(doc, dict):
                doc = Document.from_data(doc)
            elif not isinstance(doc, Document) and sale_amount == None:
                raise AvalaraTypeException(AvalaraException.CODE_BAD_DOC, 'Please pass a document or a dictionary to create a Document')
        elif sale_amount is None:
            raise AvalaraException(AvalaraException.CODE_BAD_ARGS, 'Please pass a doc argument, or sale_amount kwarg')
        try:
            stem = '/'.join([self.VERSION, 'tax', '%.6f,%.6f' % (lat, lng), 'get'])
        except TypeError:
            raise AvalaraTypeException(AvalaraException.CODE_LATLNG, 'Please pass lat and lng as floats, or Decimal')
        data = {'saleamount': sale_amount} if sale_amount else {'saleamount': doc.total}
        resp = self._get(stem, data)
        self.logger.info('"GET" %s%s with: %s' % (self.url, stem, data))
        self.recorder.success(doc)
        return GetTaxResponse(resp)

    @except_500_and_return
    def post_tax(self, doc, commit=False):
        """Performs a HTTP POST to tax/get/   If commit=True we will 
        update the document's Commit flag to True, and we will check 
        the document type to make sure it is capable of being Commited.
        XXXXXOrder is not capable of being commited. We will change it 
        to XXXXXXXInvoice, which is capable of being committed"""
        if isinstance(doc, dict):
            doc = Document.from_data(doc)
        elif not isinstance(doc, Document):
            raise AvalaraTypeException(AvalaraException.CODE_BAD_DOC, 'Please pass a document or a dictionary to create a Document')
        stem = '/'.join([self.VERSION, 'tax', 'get'])
        doc.update(CompanyCode=self.company_code)
        if commit:
            doc.update(Commit=True)
            self.logger.debug('%s setting Commit=True' % doc.DocCode)
            # need to change doctype if order, to invoice, otherwise commit does nothing
            new_doc_type = {
                Document.DOC_TYPE_SALE_ORDER: Document.DOC_TYPE_SALE_INVOICE,
                Document.DOC_TYPE_RETURN_ORDER: Document.DOC_TYPE_RETURN_INVOICE,
                Document.DOC_TYPE_PURCHASE_ORDER: Document.DOC_TYPE_PURCHASE_INVOICE,
                Document.DOC_TYPE_INVENTORY_ORDER: Document.DOC_TYPE_INVENTORY_INVOICE
            }.get(doc.DocType, None)
            if new_doc_type:
                self.logger.debug('%s updating DocType from %s to %s' % (doc.DocCode, doc.DocType, new_doc_type))
                doc.update(DocType=new_doc_type)
        data = doc.todict()
        resp = self._post(stem, data)
        tax_resp = PostTaxResponse(resp)
        self.logger.info('"POST", %s, %s%s with: %s' % (getattr(doc, 'DocCode', None), self.url, stem, data))
        if not hasattr(doc, 'DocCode'):
            doc.update_doc_code_from_response(tax_resp)
        self.recorder.success(doc)
        return tax_resp

    @except_500_and_return
    def cancel_tax(self, doc, reason=None, doc_id=None):
        """Performs a HTTP POST to tax/cancel/"""
        if isinstance(doc, dict):
            doc = Document.from_data(doc)
        elif not isinstance(doc, Document):
            raise AvalaraTypeException(AvalaraException.CODE_BAD_DOC, 'Please pass a document or a dictionary to create a Document')
        if reason and (not reason in Document.CANCEL_CODES):
            raise AvalaraValidationException(AvalaraException.CODE_BAD_CANCEL, "Please pass a valid cancel code")
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
        self.logger.info('"POST", %s, %s%s with: %s' % (getattr(doc, 'DocCode', None), self.url, stem, data))
        self.recorder.success(doc)
        return CancelTaxResponse(resp)

    @except_500_and_return
    def validate_address(self, address):
        """Performs a HTTP GET to address/validate/"""
        if isinstance(address, dict):
            address = Address.from_data(address)
        elif not isinstance(address, Address):
            raise AvalaraTypeException(AvalaraException.CODE_BAD_ADDRESS, 'Please pass an address or a dictionary to create an Address')
        stem = '/'.join([self.VERSION, 'address', 'validate'])
        resp = self._get(stem, address.todict())
        self.logger.info('"GET", %s%s with: %s' % (self.url, stem, address.todict()))
        return ValidateAddressResponse(resp)


class GetTaxResponse(BaseResponse):
    _fields = ['Rate', 'Tax', 'ResultCode']
    _contains = ['TaxDetails']

    @property
    def total_tax(self):
        return getattr(self, 'Tax', None)


class PostTaxResponse(BaseResponse):
    _fields = ['DocCode', 'DocId', 'DocDate', 'Timestamp', 'TotalAmount', 'TotalDiscount', 'TotalExemption', 'TotalTaxable', 'TotalTax', 'TotalTaxCalculated', 'TaxDate', 'ResultCode']
    _contains = ['TaxLines', 'TaxDetails', 'TaxAddresses']

    @property
    def total_tax(self):
        return getattr(self, 'TotalTax', None)


class CancelTaxResponse(BaseResponse):
    _has = ['CancelTaxResult']

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
    _fields = ['ResultCode']
    _has = ['Address']
