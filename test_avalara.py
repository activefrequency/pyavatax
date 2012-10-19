from base import Document, Line, Address
from api import API
from avalara import AvalaraException, AvalaraServerException, AvalaraServerDetailException
import settings_local
import datetime
import pytest


def get_api():
    return API(settings_local.AVALARA_ACCOUNT_NUMBER, settings_local.AVALARA_LICENSE_KEY, settings_local.AVALARA_COMPANY_CODE, live=False)


@pytest.mark.internals
def test_exceptions():
    try:
        raise AvalaraServerDetailException(None)
    except AvalaraServerException:
        assert True
        

@pytest.mark.simple_example
def test_avalara_example():
    api = get_api()
    # data example from avalara rest documentation
    data =  {
        "DocDate": "2011-05-11",
        "CustomerCode": "CUST1",
        "CompanyCode": settings_local.AVALARA_COMPANY_CODE,
        "Addresses": [ {
            "AddressCode": "1",
            "Line1": "435 Ericksen Avenue Northeast",
            "Line2": "#250",
            "PostalCode": "98110"
            }
        ],
        "Lines": [ {
            "LineNo": "1",
            "DestinationCode": "1",
            "OriginCode": "1",
            "Qty": 1,
            "Amount": 10
            }
        ]
    }
    stem = '/'.join([api.VERSION, 'tax','get'])
    resp = api._post(stem, data)
    assert resp.status_code == 200


@pytest.mark.extended_example
def test_extended_example():
    """
        To see more raw output from the avalara you can run this example
    """
    api = get_api()
    data = {
        "DocDate": "2012-06-13",
        "CompanyCode": settings_local.AVALARA_COMPANY_CODE,
        "CustomerCode": "AvaTim",
        "DocCode": "20120613-1",
        "DocType": "SalesOrder",
        "Addresses":
        [
        {
            "AddressCode": "1",
            "Line1": "435 Ericksen Avenue Northeast",
            "Line2": "#250",
            "City": "Bainbridge Island",
            "Region": "WA",
            "PostalCode": "98110",
            "Country": "US",
        },
        {               
            "AddressCode": "2",
            "Line1": "7562 Kearney St.",
            "City": "Commerce City",
            "Region": "CO",
            "PostalCode": "80022-1336",
            "Country": "US",                        
        },
        ],
        "Lines":
        [
        {
            "LineNo": "1",
            "DestinationCode": "2",
            "OriginCode": "1",
            "ItemCode": "AvaDocs",
            "Description": "Box of Avalara Documentation",
            "Qty": 1,
            "Amount": "100",
        },
        ],
    }
    stem = '/'.join([api.VERSION, 'tax','get'])
    resp = api._post(stem, data)
    assert resp.status_code == 200


@pytest.mark.get_tax
def test_gettax():
    api = get_api()
    # A Lat/Long from Avalara's documentation
    lat = 47.627935 
    lng = -122.51702
    line = Line(Amount=10.00)
    doc = Document()
    doc.add_line(line)
    tax = api.get_tax(lat, lng, doc)
    assert tax.is_success == True
    assert tax.Tax > 0


# when dealing with line items going to different addresses, i.e. a drop-ship situation
# don't use the basic add_from/add_to_address helpers just manually match your own 
# Origin and Destination codes for the addresses and line items
@pytest.mark.internals
def test_validation():
    doc = Document.new_sales_order(DocCode='1001', DocDate=datetime.date.today(), CustomerCode='email@email.com')
    try:
        doc.validate()
    except AvalaraException:
        assert True
    else:
        assert False
    from_address = Address(Line1="435 Ericksen Avenue Northeast", Line2="#250", PostalCode="98110")
    to_address = Address(Line1="435 Ericksen Avenue Northeast", Line2="#250", PostalCode="98110")
    doc.add_from_address(from_address)
    doc.add_to_address(to_address)
    try:
        doc.validate()
    except AvalaraException:
        assert True
    else:
        assert False
    try:
        doc.add_from_address(from_address)
    except AvalaraException:
        assert True
    else:
        assert False
    try:
        doc.add_to_address(from_address)
    except AvalaraException:
        assert True
    else:
        assert False
    line = Line(Amount=10.00)
    doc.add_line(line)
    try:
        doc.validate()
    except AvalaraException:
        assert False


@pytest.mark.post_tax
def test_posttax():
    api = get_api()
    # CustomerCode is just a unique identifier for a customer, often times, an email address or user id
    doc = Document.new_sales_order(DocCode='1001', DocDate=datetime.date.today(), CustomerCode='email@email.com')
    to_address = Address(Line1="435 Ericksen Avenue Northeast", Line2="#250", PostalCode="98110")
    from_address = Address(Line1="100 Ravine Lane NE", Line2="#220", PostalCode="98110")
    doc.add_from_address(from_address)
    doc.add_to_address(to_address)
    line = Line(Amount=10.00)
    doc.add_line(line)
    tax = api.post_tax(doc)
    assert tax.is_success == True 
    assert tax.TotalTax > 0
    assert len(tax.TaxAddresses) == 2
    assert len(tax.TaxLines) == 1


@pytest.mark.address
def test_validate_address():
    api = get_api()
    address = Address(Line1="435 Ericksen Avenue Northeast", Line2="#250", PostalCode="98110")
    validate = api.address_validate(address)
    assert validate.is_success == True
    assert validate.Address.Region == 'WA'

    # this is the right zip code
    address = Address(Line1="11 Endicott Ave", Line2="Apt 1", PostalCode="02144")
    validate = api.address_validate(address)
    assert validate.is_success == True
    assert validate.Address.Region == 'MA'

    #this is the wrong zip code
    address = Address(Line1="11 Endicott Ave", Line2="Apt 1", PostalCode="02139")
    validate = api.address_validate(address)
    assert validate.is_success == False
    assert len(validate.Messages) == 1
