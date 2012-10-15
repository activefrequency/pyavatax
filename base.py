from avalara import AvalaraException


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
                klass = str_to_class(k)
                if isinstance(v, klass): # we already have a python object
                    getattr(self, k).append(v)
                elif type(v) == type(dict): # map v into that class
                    getattr(self, k).append(klass(**v))
                    
                    
    def tojson(self):
        data = {}
        for f in self.__fields__:
            data[f] = getattr(self, f)
        for f in self.__contains__:
            data[f] = []
            for obj in getattr(self, f):
                data[f].append(obj.tojson())
        return data


class Document(AvalaraBase):
    DOC_TYPE_SALE_ORDER = 'SalesOrder'
    DOC_TYPE_SALE_INVOICE = 'SalesInvoice'
    DOC_TYPE_RETURN_ORDER = 'ReturnOrder'
    DOC_TYPE_RETURN_INVOICE = 'ReturnInvoice'
    DOC_TYPE_PURCHASE_ORDER = 'PurchaseOrder'
    DOC_TYPE_PURCHASE_INVOICE = 'PurchaseInvoice'
    DOC_TYPE_INVENTORY_ORDER = 'InventoryTransferOrder'
    DOC_TYPE_INVENTORY_INVOICE = 'InventoryTransferInvoice'

    __fields__ = ['DocType', 'DocCode', 'DocDate', 'CustomerCode']
    __contains__ = ['Lines', 'Addresses']

    def add_line(self, line):
        if isinstance(line, Line):
            self.Lines.append(line)
        else:
            raise AvalaraException('%r is not a %r' % (line, Line))

    def add_address(self, address):
        if isinstance(address, Address):
            self.Addresses.append(address)
        else:
            raise AvalaraException('%r is not a %r' % (address, Address))

    @property
    def total(self):
        return sum([ getattr(line, 'Amount') for line in self.Lines ])

class Line(AvalaraBase):
    __fields__ = ['LineNo', 'DestinationCode', 'OriginCode', 'Qty', 'Amount']


class Address(AvalaraBase):
    __fields__ = ['AddressCode', 'Line1', 'Line2', 'PostalCode', 'Region', 'Country', 'FipsCode', 'CarrierRoute', 'PostNet', 'AddressType']


class TaxAddresses(AvalaraBase):
    __fields__ = ['Address', 'AddressCode', 'City', 'Country', 'PostalCode', 'Region', 'TaxRegionId', 'JurisCode']


class TaxDetails(AvalaraBase):
    __fields__ = ['Country', 'Region', 'JurisType', 'Taxable', 'Rate', 'Tax', 'JurisName', 'TaxName']


class TaxLines(AvalaraBase):
    __fields__ = ['LineNo', 'TaxCode', 'Taxability', 'Taxable', 'Rate', 'Tax', 'Discount', 'TaxCalculated', 'Exemption']
    __contains__ = ['TaxDetails']


class CancelTaxRequest(AvalaraBase):
    __fields__ = ['DocId', 'TransactionId', 'ResultCode']
