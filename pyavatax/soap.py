import datetime
import suds
import socket
import logging

from pyavatax.base import AvalaraBase, ErrorResponse, AvalaraException, AvalaraBaseException
from pyavatax.django_integration import get_django_recorder


class AvaTaxSoapAPI(object):
    live_wsdl = 'https://avatax.avalara.net/Tax/taxsvc.wsdl'
    dev_wsdl = 'https://development.avalara.net/Tax/taxsvc.wsdl'
    dev_url = 'https://development.avalara.net'
    live_url = 'https://avatax.avalara.net'

    def __init__(self, username, password, live=False, logger=None, recorder=None, *args, **kwargs):
        self.username = username
        self.password = password
        if logger is None:
            logger = logging.getLogger('pyavatax.api')
        self.logger = logger
        if recorder is None:
            recorder = get_django_recorder()
        self.recorder = recorder
        wsdl = AvaTaxSoapAPI.live_wsdl if live else AvaTaxSoapAPI.dev_wsdl
        self.url = AvaTaxSoapAPI.live_url if live else AvaTaxSoapAPI.dev_url
        self.client = suds.client.Client(wsdl)
        self._setup_client()

    def _setup_client(self):
        nameCap = 'Tax'
        self.client.set_options(service='%sSvc' % nameCap)
        self.client.set_options(port='%sSvcSoap' % nameCap)
        self.client.set_options(location='%s/%s/%sSvc.asmx' % (self.url, nameCap, nameCap))
        self.client.set_options(wsse=self._get_credentials(self.username, self.password))
        self.client.set_options(soapheaders=self._my_profile())

    def _get_credentials(self, username, password):
        token = suds.wsse.UsernameToken(username, password)
        token.setcreated()
        #token.setnonce()
        security = suds.wsse.Security()
        security.tokens.append(token)
        return security

    def _my_profile(self):
        ADAPTER = 'PyAvaTax,0.1'
        CLIENT = 'PyAvaTaxSoap,0.1'
        profileNameSpace = ('ns1', 'http://avatax.avalara.com/services')
        profile = suds.sax.element.Element('Profile', ns=profileNameSpace)
        profile.append(suds.sax.element.Element('Client', ns=profileNameSpace).setText(CLIENT))
        profile.append(suds.sax.element.Element('Adapter', ns=profileNameSpace).setText(ADAPTER))
        hostname = socket.gethostname()
        profile.append(suds.sax.element.Element('Machine', ns=profileNameSpace).setText(hostname))
        return profile

    def translate_obj_to_soap(self, doc, soap_doc):
        doc.validate()
        for f in doc._fields:
            if hasattr(doc, f):
                setattr(soap_doc, f, getattr(doc, f))
        _addy = []
        for a in doc.Addresses:
            addy = self.client.factory.create('BaseAddress')
            addy.TaxRegionId = 0  # a soap default
            for f in a._fields:
                if hasattr(a, f):
                    setattr(addy, f, getattr(a, f))
            _addy.append(addy)
        addresses = self.client.factory.create('ArrayOfBaseAddress')
        addresses.BaseAddress = _addy
        soap_doc.Addresses = addresses
        _line = []
        for l in doc.Lines:
            line = self.client.factory.create('Line')
            for f in l._fields:
                if hasattr(l, f):
                    _f = 'No' if f == 'LineNo' else f  # hack :/
                    setattr(line, _f, getattr(l, f))
            line.Discounted = False
            _line.append(line)
        lines = self.client.factory.create('ArrayOfLine')
        lines.Line = _line
        soap_doc.Lines = lines

    def set_soap_defaults(self, soap_doc):
        soap_doc.DetailLevel = 'Line'
        soap_doc.HashCode = 0
        soap_doc.ServiceMode = 'Remote'
        soap_doc.PaymentDate = '1900-01-01'
        soap_doc.ExchangeRate = 0
        soap_doc.ExchangeRateEffDate = '1900-01-01'

    def tax_override(self, doc, tax_date=None, tax_amt=None, override_type=None, reason=None):
        if getattr(doc, 'Commit', False):
            raise AvalaraException('You cannot override an already commited document')
        override = self.client.factory.create('TaxOverride')
        if isinstance(tax_date, str):
            override.TaxDate = tax_date
        elif isinstance(tax_date, datetime.date):
            override.TaxDate = tax_date.isoformat()
        override.Reason = reason
        override.TaxOverrideType = override_type
        override.TaxAmount = tax_amt

        soap_doc = self.client.factory.create('GetTaxRequest')
        self.translate_obj_to_soap(doc, soap_doc)
        self.set_soap_defaults(soap_doc)
        soap_doc.TaxOverride = override
        soap_doc.Commit = True  # necessary
        resp = self.send(self.client.service.GetTax, soap_doc, doc)
        if isinstance(resp, AvalaraSoapErrorResponse):
            return resp
        tax = TaxOverrideResponse(resp)
        self.logger.info('"POST" TaxOverride - %s' % (doc.DocCode))
        self.recorder.success(doc)
        return tax

    def send(self, operation, soap_obj, doc):
        try:
            result = operation(soap_obj)
        except suds.WebFault as e:
            self.logger.error("Data: %r \n Errors: %r" % (repr(soap_obj), repr(e)))
            e = AvalaraSoapErrorResponse(None, e)
            self.recorder.failure(doc, e)
            return e
        else:
            if (result.ResultCode != 'Success'):
                e = AvalaraSoapErrorResponse(result)
                self.logger.error(e)
                self.recorder.failure(doc, e)
                return e
            else:
                return result


class AvalaraSoapErrorResponse(ErrorResponse):

    def __init__(self, result, *args, **kwargs):
        self.response = None
        self.error = None
        if isinstance(result, AvalaraBaseException):
            self.response = result
        else:
            self.error = args[0]

    @property
    def is_success(self):
        return False

    @property
    def _details(self):
        return self.response.Messages if self.response else self.error

    def error(self):
        return self._details

    def __str__(self):
        return self._details


class TaxOverrideResponse(AvalaraBase):

    def __init__(self, soap_response, *args, **kwargs):
        self.response = soap_response

    @property
    def is_success(self):
        return True if self.response.ResultCode == 'Success' else False

    @property
    def total_tax(self):
        return self.response.TotalTax
