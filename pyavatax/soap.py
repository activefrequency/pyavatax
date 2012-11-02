import suds
import socket
from pyavatax.base import AvalaraBase, AvalaraException, AvalaraBaseException


class AvaTaxSoapAPI(object):
    live_wsdl = 'https://avatax.avalara.net/Tax/taxsvc.wsdl'
    dev_wsdl = 'https://development.avalara.net/Tax/taxsvc.wsdl'
    dev_url = 'https://development.avalara.net'
    live_url = 'https://avatax.avalara.net'

    def __init__(self, username, password, live=False, *args, **kwargs):
        self.username = username
        self.password = password
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
        # AvaTax leaves the WSSE Nonce and Created elements as
        # optional. As explained in XXX, you should include these if at
        # all possible, to make your connection more secure.
        # Nonce (optional) is a randomly generated, cryptographic token
        # used to prevent theft and replay attacks. We recommend sending
        # it if your SOAP client library supports it.
        token.setnonce()
        # Created (optional) identifies when the message was created and
        # prevents replay attacks. We recommend sending it if your SOAP
        # client library supports it.
        token.setcreated()
        security = suds.wsse.Security()
        security.tokens.append(token)
        return security

    def _my_profile(self):

        # First set elements that the adapters set meaningful defaults
        # for. Essentially, you are rolling your own Python adapter so
        # make this clear in the Adapter element.

        ADAPTER = 'AvalaraPython,0.1'
        CLIENT = 'Playtime,0.1'

        # Build the Profile element

        profileNameSpace = ('ns1', 'http://avatax.avalara.com/services')
        profile = suds.sax.element.Element('Profile', ns=profileNameSpace)
        profile.append(suds.sax.element.Element('Client', ns=profileNameSpace).setText(CLIENT))
        profile.append(suds.sax.element.Element('Adapter', ns=profileNameSpace).setText(ADAPTER))

        hostname = socket.gethostname()
        profile.append(suds.sax.element.Element('Machine', ns=profileNameSpace).setText(hostname))

        return profile

    def translate_obj_to_soap(self, doc, soap_doc):
        doc.validate()
        for f in doc.__fields__:
            if hasattr(doc, f):
                setattr(soap_doc, f, getattr(doc, f))
        _addy = []
        for a in doc.Addresses:
            addy = self.client.factory.create('BaseAddress')
            addy.TaxRegionId = 0  # a soap default
            for f in a.__fields__:
                if hasattr(a, f):
                    setattr(addy, f, getattr(a, f))
            _addy.append(addy)
        addresses = self.client.factory.create('ArrayOfBaseAddress')
        addresses.BaseAddress = _addy
        soap_doc.Addresses = addresses
        _line = []
        for l in doc.Lines:
            line = self.client.factory.create('Line')
            for f in l.__fields__:
                if hasattr(l, f):
                    _f = 'No' if f == 'LineNo' else f  # hack :/
                    setattr(line, _f, getattr(l, f))
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
        override.TaxDate = tax_date
        override.Reason = reason
        override.TaxOverrideType = override_type
        override.TaxAmount = tax_amt

        soap_doc = self.client.factory.create('GetTaxRequest')
        self.translate_obj_to_soap(doc, soap_doc)
        self.set_soap_defaults(soap_doc)
        soap_doc.TaxOverride = override
        soap_doc.Commit = True  # necessary
        return TaxOverrideResponse(self.send(self.client.service.GetTax, soap_doc))

    def send(self, operation, soap_obj):
        try:
            result = operation(soap_obj)
        except suds.WebFault as e:
            raise AvalaraSoapServerException(e)
        else:
            if (result.ResultCode != 'Success'):
                raise AvalaraSoapServerException(result)
            else:
                return result


class AvalaraSoapServerException(AvalaraBaseException):

    def __init__(self, result, *args, **kwargs):
        super(AvalaraSoapServerException, self).__init__(*args, **kwargs)
        if not isinstance(result, AvalaraBaseException):
            self.response = result

    def is_success(self):
        return False

    @property
    def _details(self):
        return self.response.Messages

    def error(self):
        return self._details

    def __str__(self):
        return self._details


class TaxOverrideResponse(AvalaraBase):

    def __init__(self, soap_response, *args, **kwargs):
        self.response = soap_response

    @property
    def total_tax(self):
        return self.response.TotalTax
