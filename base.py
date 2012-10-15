from avalara import AvalaraException, AvalaraBase


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
