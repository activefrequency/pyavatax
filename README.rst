PyAvaTax
=========

What is PyAvaTax?
------------------

`Avalara <http://www.avalara.com/>`_ offers a fully featured web-based service to report your transactions, return your sales tax, and store all the information until you need to report it.

We developed PyAvaTax as a Python client library for easily integrating with Avalara's RESTful AvaTax API Service to report your transactions.

PyAvaTax **does not require Django**, though if you are using a Django system we have some admin-based goodies for you to check out (Django >= 1.6, `see why <https://pyavatax.readthedocs.org/en/latest/django.html>`_ )!

This API is not officially supported by Avalara - it is a third-party library developed and supported by `Active Frequency <http://www.activefrequency.com/>`_.

Please report bugs using the GitHub issue tracker.

Usage
-----

***Note***: Avalara is a US-only service, and thus all amounts passing through their system, and this API, are assumed to be US Dollars (USD)


AvaTax expects a JSON (or XML) POST to their tax/get/ URI, like this:
::
    {
        "DocDate": "2012-10-24",
        "CompanyCode": "FooBar",
        "CustomerCode": "email@example.com",
        "DocCode": "1001",
        "DocType": "SalesOrder",
        "Addresses":
        [
            {
                "AddressCode": "1",
                "Line1": "435 Ericksen Avenue Northeast",
                "Line2": "#250",
                "PostalCode": "98110"
            },
            {
                "AddressCode": "2",
                "Line1": "7562 Kearney St.",
                "PostalCode": "80022-1336"
            }
        ],
        "Lines":
        [
            {
                "LineNo": "1",
                "DestinationCode": "2",
                "OriginCode": "1",
                "Qty": 1,
                "Amount": "100"
            }
        ]
    }

Our library, accepts your data in a variety of ways. You instantiate the API like so
::
    api = API(AVALARA_ACCOUNT_NUMBER, AVALARA_LICENSE_KEY, AVALARA_COMPANY_CODE)

Then, you can perform an action (e.g. "Post Tax"), by passing in a data dictionary. We will parse it, validate it, handle the HTTP layer for you, and return a response object to you.
::
    tax_response = api.post_tax(dictionary_data)
    print tax_response.TotalTax  # this is unicode 
    >>> 0.86

That returned object will have all the response data from AvaTax easily accessible by dot-notation.

Or, you can use the library to construct objects from kwargs
::
    api = API(AVALARA_ACCOUNT_NUMBER, AVALARA_LICENSE_KEY, AVALARA_COMPANY_CODE)
    doc = Document.new_sales_order(DocCode='1001', DocDate=datetime.date.today(), CustomerCode='email@example.com')
    from_address = Address(Line1="435 Ericksen Avenue Northeast", Line2="#250", PostalCode="98110")
    to_address = Address(Line1="7562 Kearney St.", PostalCode="80022-1336")
    doc.add_from_address(from_address)
    doc.add_to_address(to_address)
    line = Line(Amount=10.00)
    doc.add_line(line)
    response = api.post_tax(doc)


Further Reading
---------------

Documentation is in *docs*, or at https://pyavatax.readthedocs.org/en/latest/; see *Advanced* (https://pyavatax.readthedocs.org/en/latest/advanced.html) for instructions on running the test suite.
