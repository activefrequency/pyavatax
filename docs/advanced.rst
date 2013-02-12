.. _advanced:

Advanced
========

SOAP -- There Be Dragons Here
---------------------------------

The AvaTax REST API is not fully functional yet as compared to their SOAP API. They don't have an approved Python interface (what they call a "connector") overlaying the SOAP interface. They have Java, .NET, and PHP interfaces.

The REST API is getting a host of features in 2013. In the meantime, we've put together a simple SOAP API layer.

Similar and simple instantiation:
::
    api = AvaTaxSoapAPI(AVALARA_ACCOUNT_NUMBER, AVALARA_LICENSE_KEY, live=False)


I've only implemented a TaxOverride call because that is all I needed at the time. Using the SOAP interface looks like this:
::
    doc = Document.new_sales_invoice(DocCode=random_doc_code, DocDate=datetime.date.today(), CustomerCode='email@email.com')
    to_address = Address(Line1="435 Ericksen Avenue Northeast", Line2="#250", PostalCode="98110")
    from_address = Address(Line1="100 Ravine Lane NE", Line2="#220", PostalCode="98110")
    doc.add_from_address(from_address)
    doc.add_to_address(to_address)
    line = Line(Amount=10.00)
    doc.add_line(line)
    tax_date = datetime.date.today() - datetime.timedelta(days=5)  # change the taxable date to five days ago
    tax = soap_api.tax_override(doc, tax_date=tax_date, tax_amt=0, reason="Tax Date change", override_type='TaxDate')
    print tax.total_tax


If you have to use the SOAP API, you probably know what you're doing. If you don't know what you're doing you probably don't need to use SOAP.

If you need other SOAP features that Avalara hasn't opened up in the REST API feel free to fork, and roll your own.


Running the Tests
-----------------

If you're working with the source code and want to run our tests, you can run the test suite (we are using pytest).

There are some tests specifically for the Django features. If you're not running in a Django environment, those specific tests will fail; that is expected.

The test script uses a ``settings_local.py`` secrets file that isn't included in this package.  We've included a ``settings_local.py.example`` file that you can copy into ``settings_local.py`` and update with your credentials.

If you have a Django environment you can run ``manage.py shell`` locally and then this:
::
    >>> import pytest
    >>> pytest.main('path/to/pyavatax/test_avalara.py')

Alternatively, you can just do:
::
    $ py.test
