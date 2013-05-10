from pyavatax.base import Document, Line, Address, TaxOverride, AvalaraException, AvalaraTypeException, AvalaraValidationException, AvalaraServerNotReachableException
from pyavatax.api import API
import settings_local  # put the below settings into this file, it is in .gitignore
import datetime
import pytest
from testfixtures import LogCapture


def get_api(timeout=None):
    return API(settings_local.AVALARA_ACCOUNT_NUMBER, settings_local.AVALARA_LICENSE_KEY, settings_local.AVALARA_COMPANY_CODE, live=False, timeout=timeout)


@pytest.mark.example
def test_avalara_and_http():
    api = get_api()
    data = {
        "DocDate": "2012-05-11",
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
@pytest.mark.from_data
def test_from_data_example():
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
    tax = api.post_tax(data)
    assert tax.is_success is True


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
    assert tax.total_tax == tax.Tax
    tax = api.get_tax(lat, lng, None, sale_amount=10.00)
    assert tax.is_success is True
    assert tax.Tax > 0
    assert tax.total_tax == tax.Tax


# when dealing with line items going to different addresses, i.e. a drop-ship situation
# don't use the basic add_from/add_to_address helpers just manually match your own
# Origin and Destination codes for the addresses and line items
@pytest.mark.internals
def test_validation():
    with pytest.raises(AvalaraValidationException) as e:
        doc = Document(DocDate='foo')  # testing date
    assert e.value.code == AvalaraException.CODE_BAD_DATE
    with pytest.raises(AvalaraValidationException) as e:
        line = Line(Qty='foo')  # testing int
    assert e.value.code == AvalaraException.CODE_BAD_FLOAT
    with pytest.raises(AvalaraValidationException) as e:
        line = Line(Amount='foo')  # testing float
    assert e.value.code == AvalaraException.CODE_BAD_FLOAT
    with pytest.raises(AvalaraValidationException) as e:
        line = Line(ItemCode='this string is longer than fifty characters and should be stopped')  # testing length
    assert e.value.code == AvalaraException.CODE_TOO_LONG
    doc = Document.new_sales_order(DocCode='1001', DocDate=datetime.date.today(), CustomerCode='email@email.com')
    with pytest.raises(AvalaraValidationException) as e:
        doc.validate()
    assert e.value.code == AvalaraException.CODE_BAD_ADDRESS
    from_address = Address(Line1="435 Ericksen Avenue Northeast", Line2="#250", PostalCode="98110")
    to_address = Address(Line1="435 Ericksen Avenue Northeast", Line2="#250", PostalCode="98110")
    doc.add_from_address(from_address)
    doc.add_to_address(to_address)
    with pytest.raises(AvalaraValidationException) as e:
        doc.validate()
    assert e.value.code == AvalaraException.CODE_BAD_LINE
    with pytest.raises(AvalaraException) as e:
        doc.add_from_address(from_address)
    assert e.value.code == AvalaraException.CODE_HAS_FROM
    with pytest.raises(AvalaraException) as e:
        doc.add_to_address(to_address)
    assert e.value.code == AvalaraException.CODE_HAS_TO
    line = Line(Amount=10.00)
    doc.add_line(line)
    doc.validate()
    api = get_api()
    lat = 47.627935
    lng = -122.51702
    with pytest.raises(AvalaraTypeException) as e:
        api.get_tax(lat, lng, 'foo', None)
    assert e.value.code == AvalaraException.CODE_BAD_DOC
    with pytest.raises(AvalaraException) as e:
        api.get_tax(lat, lng, None, None)
    assert e.value.code == AvalaraException.CODE_BAD_ARGS


@pytest.mark.post_tax
@pytest.mark.logging
def test_posttax():
    with LogCapture('pyavatax.api') as l:
        api = get_api()
        # dont pass a doccode
        doc = Document.new_sales_order(DocDate=datetime.date.today(), CustomerCode='email@email.com')
        doc.add_from_address(Line1="100 Ravine Lane NE", Line2="#220", PostalCode="98110")
        doc.add_to_address(Line1="435 Ericksen Avenue Northeast", Line2="#250", PostalCode="98110")
        doc.add_line(Amount=10.00)
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
    l.check(
        ('pyavatax.api', 'DEBUG', 'None setting default from address code'),
        ('pyavatax.api', 'DEBUG', 'None setting default to address code'),
        ('pyavatax.api', 'DEBUG', 'None inserting LineNo 1'),
        ('pyavatax.api', 'DEBUG', 'None setting origin code %s' % Address.DEFAULT_FROM_ADDRESS_CODE),
        ('pyavatax.api', 'DEBUG', 'None setting destination code %s' % Address.DEFAULT_TO_ADDRESS_CODE),
        ('pyavatax.api', 'INFO', '"POST", %s, %s%s' % (None, api.url, '/'.join([API.VERSION, 'tax', 'get']))),
        ('pyavatax.api', 'DEBUG', 'AvaTax assigned %s as DocCode' % doc.DocCode)
    )


@pytest.mark.logging
def test_timeout():
    with LogCapture('pyavatax.api') as l:
        api = get_api(timeout=0.00001)
        lat = 47.627935
        lng = -122.51702
        line = Line(Amount=10.00)
        doc = Document()
        doc.add_line(line)
        try:
            api.get_tax(lat, lng, doc)
        except AvalaraServerNotReachableException:
            assert True
        else:
            assert False
    l.check(
        ('pyavatax.api', 'DEBUG', 'None inserting LineNo 1'),
        ('pyavatax.api', 'ERROR', "HTTPSConnectionPool(host='development.avalara.net', port=443): Request timed out. (timeout=1e-05)")
    )


@pytest.mark.post_tax
@pytest.mark.cancel_tax
def test_posttax_commit_cancel():
    import uuid
    random_doc_code = uuid.uuid4().hex  # you can't post/cancel the same doc code over and over
    api = get_api()
    doc = Document.new_sales_order(DocCode=random_doc_code, DocDate=datetime.date.today(), CustomerCode='email@email.com')
    to_address = Address(Line1="435 Ericksen Avenue Northeast", Line2="#250", PostalCode="98110")
    from_address = Address(Line1="100 Ravine Lane NE", Line2="#220", PostalCode="98110")
    doc.add_from_address(from_address)
    doc.add_to_address(to_address)
    line = Line(Amount=10.00)
    doc.add_line(line)
    tax = api.post_tax(doc, commit=True)
    assert doc.Commit
    assert doc.DocType == Document.DOC_TYPE_SALE_INVOICE  # make sure the doc type changes with commit
    assert tax.is_success is True
    assert tax.TotalTax > 0
    assert tax.total_tax == tax.TotalTax
    assert len(tax.TaxAddresses) == 2
    assert len(tax.TaxLines) == 1
    assert len(tax.TaxLines[0].TaxDetails) > 0
    cancel = api.cancel_tax(doc)
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


@pytest.mark.override
def test_override():
    import uuid
    with LogCapture() as l:
        random_doc_code = uuid.uuid4().hex  # you can't post/cancel the same doc code over and over
        api = get_api()
        doc = Document.new_sales_invoice(DocCode=random_doc_code, DocDate=datetime.date.today(), CustomerCode='email@email.com')
        to_address = Address(Line1="435 Ericksen Avenue Northeast", Line2="#250", PostalCode="98110")
        from_address = Address(Line1="100 Ravine Lane NE", Line2="#220", PostalCode="98110")
        doc.add_from_address(from_address)
        doc.add_to_address(to_address)
        line = Line(Amount=10.00)
        doc.add_line(line)
        tax_date = datetime.date.today() - datetime.timedelta(days=5)
        doc.add_override(TaxOverrideType=TaxOverride.OVERRIDE_DATE, TaxDate=tax_date, Reason="Tax Date change",)
        tax = api.post_tax(doc)
        assert tax.is_success
        assert tax.total_tax > 0
        assert tax.TaxDate == tax_date.strftime('%Y-%m-%d')


@pytest.mark.override
@pytest.mark.recorder
@pytest.mark.failure_case
def test_override_failure():
    try:
        from pyavatax.models import AvaTaxRecord
    except ImportError:  # no django
        pytest.mark.xfail('This can only be run inside a django environment')
        return
    import uuid
    random_doc_code = uuid.uuid4().hex  # you can't post/cancel the same doc code over and over
    api = get_api()
    doc = Document.new_sales_invoice(DocCode=random_doc_code, DocDate=datetime.date.today(), CustomerCode='email@email.com')
    to_address = Address(Line1="435 Ericksen Avenue Northeast", Line2="#250", PostalCode="98110")
    from_address = Address(Line1="100 Ravine Lane NE", Line2="#220", PostalCode="98110")
    doc.add_from_address(from_address)
    doc.add_to_address(to_address)
    line = Line(Amount=10.00)
    doc.add_line(line)
    doc.DocType = 'FooBar'  # forcing error
    tax_date = datetime.date.today() - datetime.timedelta(days=5)
    doc.add_override(TaxOverrideType=TaxOverride.OVERRIDE_DATE, TaxDate=tax_date, Reason="Tax Date change",)
    tax = api.post_tax(doc)
    assert tax.is_success == False
    assert 1 == AvaTaxRecord.failures.filter(doc_code=random_doc_code).count()
    assert 0 == AvaTaxRecord.successes.filter(doc_code=random_doc_code).count()


@pytest.mark.failure_case
@pytest.mark.recorder
# this gets run from inside a django environment
def test_recorder():
    try:
        from pyavatax.models import AvaTaxRecord
    except ImportError:  # no django
        pytest.mark.xfail('This can only be run inside a django environment')
        return
    import uuid
    random_doc_code = uuid.uuid4().hex  # you can't post/cancel the same doc code over and over
    api = get_api()
    doc = Document.new_sales_invoice(DocCode=random_doc_code, DocDate=datetime.date.today(), CustomerCode='email@email.com')
    to_address = Address(Line1="435 Ericksen Avenue Northeast", Line2="#250", PostalCode="98110")
    from_address = Address(Line1="100 Ravine Lane NE", Line2="#220", PostalCode="98110")
    doc.add_from_address(from_address)
    doc.add_to_address(to_address)
    line = Line(Amount=10.00)
    doc.add_line(line)
    setattr(doc, '_testing_ignore_validate', True)  # passthrough I put in to allow this test, never actually use this
    orig_doc_type = doc.DocType
    doc.DocType = 'DoesntExist'  # forcing error
    tax = api.post_tax(doc)
    assert tax.is_success == False
    assert 1 == AvaTaxRecord.failures.filter(doc_code=random_doc_code).count()
    assert 0 == AvaTaxRecord.successes.filter(doc_code=random_doc_code).count()
    doc.DocType = orig_doc_type
    tax = api.post_tax(doc, commit=True)
    assert tax.is_success == True
    assert 0 == AvaTaxRecord.failures.filter(doc_code=random_doc_code).count()
    assert 1 == AvaTaxRecord.successes.filter(doc_code=random_doc_code).count()
    tax = api.post_tax(doc, commit=True)
    assert tax.is_success == False
    assert 1 == AvaTaxRecord.failures.filter(doc_code=random_doc_code).count()
    assert 1 == AvaTaxRecord.successes.filter(doc_code=random_doc_code).count()
