from avalara import AvalaraException, AvalaraBase


# this func needs to live here
def str_to_class(field):
    import sys
    import types
    try:
        identifier = getattr(sys.modules[__name__], field)
    except AttributeError:
        raise NameError("%s doesn't exist." % field)
    if isinstance(identifier, (types.ClassType, types.TypeType)):
        return identifier
    raise TypeError("%s is not a class." % field)


class Document(AvalaraBase):
    DOC_TYPE_SALE_ORDER = 'SalesOrder'
    DOC_TYPE_SALE_INVOICE = 'SalesInvoice'
    DOC_TYPE_RETURN_ORDER = 'ReturnOrder'
    DOC_TYPE_RETURN_INVOICE = 'ReturnInvoice'
    DOC_TYPE_PURCHASE_ORDER = 'PurchaseOrder'
    DOC_TYPE_PURCHASE_INVOICE = 'PurchaseInvoice'
    DOC_TYPE_INVENTORY_ORDER = 'InventoryTransferOrder'
    DOC_TYPE_INVENTORY_INVOICE = 'InventoryTransferInvoice'
    CANCEL_UNSPECIFIED = 'Unspecified'
    CANCEL_POST_FAILED = 'PostFailed'
    CANCEL_DOC_DELETED = 'DocDeleted'
    CANCEL_DOC_VOIDED = 'DocVoided'
    CANCEL_ADJUSTMENT_CANCELED = 'AdjustmentCanceled'
    CANCEL_CODES = ( CANCEL_UNSPECIFIED, CANCEL_POST_FAILED, CANCEL_DOC_DELETED, CANCEL_DOC_VOIDED, CANCEL_ADJUSTMENT_CANCELED )

    __fields__ = ['DocType', 'DocId', 'DocCode', 'DocDate', 'CompanyCode', 'CustomerCode', 'Discount', 'Commit', 'CustomerUsageType','PurchaseOrderNo', 'ExemptionNo', 'PaymentDate', 'ReferenceCode']
    __contains__ = ['Lines', 'Addresses' ] # the automatic parsing in `def update` doesn't work here, but its never invoked here
    __has__ = ['DetailLevel']

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

    def set_detail_level(self, detail_level):
        if isinstance(detail_level, DetailLevel):
            setattr(self, 'DetailLevel', detail_level)
        else:
            raise AvalaraException('%r is not a %r' % (detail_level, DetailLevel))
            
    def add_line(self, line):
        if isinstance(line, Line):
            if not hasattr(line, 'LineNo'):
                count = len(self.Lines)
                setattr(line, 'LineNo', count + 1) #start at one
            self.Lines.append(line)
        else:
            raise AvalaraException('%r is not a %r' % (line, Line))

    def add_from_address(self, address):
        if hasattr(self, 'from_address_code'):
            raise AvalaraException('You have already set a from address. If you are doing something beyond a simple order, just use the `add_address` method')
        if isinstance(address, Address):
            if not hasattr(address, 'AddressCode'):
                setattr(address, 'AddressCode', Address.DEFAULT_FROM_ADDRESS_CODE)
            self.from_address_code = getattr(address, 'AddressCode')
            self.Addresses.append(address)
        else:
            raise AvalaraException('%r is not a %r' % (address, Address))

    def add_to_address(self, address):
        if hasattr(self, 'to_address_code'):
            raise AvalaraException('You have already set a to address. If you are doing something beyond a simple order, just use the `add_address` method')
        if isinstance(address, Address):
            if not hasattr(address, 'AddressCode'):
                setattr(address, 'AddressCode', Address.DEFAULT_TO_ADDRESS_CODE)
            self.to_address_code = getattr(address, 'AddressCode')
            self.Addresses.append(address)
        else:
            raise AvalaraException('%r is not a %r' % (address, Address))

    def add_address(self, address):
        if isinstance(address, Address):
            self.Address.append(address)
        else:
            raise AvalaraException('%r is not a %r' % (address, Address))

    # look through line items making sure that origin and destination codes are set
    # set defaults if they exist, raise exception if we are missing something
    def validate_codes(self):
        for line in self.Lines:
            if not hasattr(line, 'OriginCode'):
                if hasattr(self, 'from_address_code'):
                    line.OriginCode = self.from_address_code
                else:
                    raise AvalaraException('Origin Code needed for Line Item %r' % line.LineNo)
            if not hasattr(Line, 'DestinationCode'):
                if hasattr(self, 'to_address_code'):
                    line.DestinationCode = self.to_address_code
                else:
                    raise AvalaraException('DestinationCode needed for Line Item %r' % line.LineNo)

    def validate(self):
        if len(self.Addresses) == 0:
            raise AvalaraException('You need Addresses')
        if len(self.Lines) == 0:
            raise AvalaraException('You need Line Items')
        self.validate_codes()

    @property
    def total(self):
        return sum([ getattr(line, 'Amount') for line in self.Lines ])


class Line(AvalaraBase):
    __fields__ = ['LineNo', 'DestinationCode', 'OriginCode', 'Qty', 'Amount', 'ItemCode', 'TaxCode', 'CustomerUsageType', 'Description', 'Discounted', 'TaxIncluded', 'Ref1', 'Ref2']

    def __init__(self, *args, **kwargs):
        if not kwargs.has_key('Qty'):
            kwargs.update({'Qty': 1})
        return super(Line, self).__init__(*args, **kwargs)


class Address(AvalaraBase):
    DEFAULT_FROM_ADDRESS_CODE = "1"
    DEFAULT_TO_ADDRESS_CODE = "2"
    __fields__ = ['AddressCode', 'Line1', 'Line2', 'Line3', 'Latitude', 'Longitude', 'PostalCode', 'Region', 'TaxRegionId', 'Country', 'AddressType', 'County', 'FipsCode', 'CarrierRoute', 'TaxRegionId', 'PostNet']

    @property
    def describe_address_type(self):
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
    __fields__ = ['Summary', 'RefersTo', 'Source', 'Details', 'Severity']


class DetailLevel(AvalaraBase):
    __fields__ = ['Line', 'Summary', 'Document', 'Tax', 'Diagnostic']


class TaxAddresses(AvalaraBase):
    __fields__ = ['Address', 'AddressCode', 'Latitude', 'Longitude', 'City', 'Country', 'PostalCode', 'Region', 'TaxRegionId', 'JurisCode']
    __contains__ = ['TaxDetails']


class TaxDetails(AvalaraBase):
    __fields__ = ['Country', 'Region', 'JurisType', 'Taxable', 'Rate', 'Tax', 'JurisName', 'TaxName']


class TaxLines(AvalaraBase):
    __fields__ = ['LineNo', 'TaxCode', 'Taxability', 'Taxable', 'Rate', 'Tax', 'Discount', 'TaxCalculated', 'Exemption']
    __contains__ = ['TaxDetails']


class CancelTaxResult(AvalaraBase):
    __fields__ = ['DocId', 'TransactionId', 'ResultCode']


