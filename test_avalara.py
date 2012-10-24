from avalara.base import Document, Line, Address, AvalaraException
from avalara.api import API
import settings_local  # put the below settings into this file, it is in .gitignore
import datetime
import pytest


def get_api():
    return API(settings_local.AVALARA_ACCOUNT_NUMBER, settings_local.AVALARA_LICENSE_KEY, settings_local.AVALARA_COMPANY_CODE, live=False)


@pytest.mark.example
def test_avalara_example():
    api = get_api()
    data = {
        "DocDate": "2011-05-11",
        "CustomerCode": "CUST1",
        "CompanyCode": settings_local.AVALARA_COMPANY_CODE,
        "Addresses":
        [
            {
                "AddressCode": "1",
                "Line1": "435 Ericksen Avenue Northeast",
                "Line2": "#250",
                "PostalCode": "98110"
            }
        ],
        "Lines":
        [
            {
                "LineNo": "1",
                "DestinationCode": "1",
                "OriginCode": "1",
                "Qty": 1,
                "Amount": 10
            }
        ]
    }
    stem = '/'.join([api.VERSION, 'tax', 'get'])
    resp = api._post(stem, data)
    assert resp.status_code == 200


@pytest.mark.example
def test_extended_example():
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
    stem = '/'.join([api.VERSION, 'tax', 'get'])
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
    assert tax.is_success is True
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
    # dont pass a doccode
    doc = Document.new_sales_order(DocDate=datetime.date.today(), CustomerCode='email@email.com')
    to_address = Address(Line1="435 Ericksen Avenue Northeast", Line2="#250", PostalCode="98110")
    from_address = Address(Line1="100 Ravine Lane NE", Line2="#220", PostalCode="98110")
    doc.add_from_address(from_address)
    doc.add_to_address(to_address)
    line = Line(Amount=10.00)
    doc.add_line(line)
    # make sure i don't have a doccode
    try:
        doc.DocCode
    except AttributeError:
        assert True
    else:
        assert False
    tax = api.post_tax(doc)
    assert tax.is_success is True
    assert tax.TotalTax > 0
    assert len(tax.TaxAddresses) == 2
    assert len(tax.TaxLines) == 1
    assert len(tax.TaxLines[0].TaxDetails) > 0
    assert tax.DocCode
    assert doc.DocCode  # make sure the doccode moved over


@pytest.mark.post_tax
@pytest.mark.cancel_tax
def test_posttax_commit_cancel():
    import uuid
    import time
    api = get_api()
    random_doc_code = uuid.uuid4().hex  # you can't post/cancel the same doc code over and over
    doc = Document.new_sales_order(DocCode=random_doc_code, DocDate=datetime.date.today(), CustomerCode='email@email.com')
    to_address = Address(Line1="435 Ericksen Avenue Northeast", Line2="#250", PostalCode="98110")
    from_address = Address(Line1="100 Ravine Lane NE", Line2="#220", PostalCode="98110")
    doc.add_from_address(from_address)
    doc.add_to_address(to_address)
    line = Line(Amount=10.00)
    doc.add_line(line)
    tax = api.post_tax(doc, commit=True)
    assert doc.Commit
    assert tax.is_success is True
    assert tax.TotalTax > 0
    assert len(tax.TaxAddresses) == 2
    assert len(tax.TaxLines) == 1
    assert len(tax.TaxLines[0].TaxDetails) > 0
    doc.DocType = Document.DOC_TYPE_SALE_INVOICE
    time.sleep(10)  # let avalara system catch up
    cancel = api.cancel_tax(doc)
    print cancel.response.request.data
    print cancel.error
    assert cancel.is_success is True
    assert cancel.CancelTaxResult


@pytest.mark.address
def test_validate_address():
    api = get_api()
    address = Address(Line1="435 Ericksen Avenue Northeast", Line2="#250", PostalCode="98110")
    validate = api.validate_address(address)
    assert validate.is_success is True
    assert validate.Address.Region == 'WA'

    # this is the right zip code
    address = Address(Line1="11 Endicott Ave", Line2="Apt 1", PostalCode="02144")
    validate = api.validate_address(address)
    assert validate.is_success is True
    assert validate.Address.Region == 'MA'


@pytest.mark.address
@pytest.mark.failure_case
def test_failure_validate_address():
    #this is the wrong zip code
    api = get_api()
    address = Address(Line1="11 Endicott Ave", Line2="Apt 1", PostalCode="02139")
    validate = api.validate_address(address)
    assert validate.is_success is False
    assert len(validate.Messages) == 1
    assert len(validate.error) == 1
