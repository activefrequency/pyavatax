PyAvaTax
========

PyAvaTax is a Python library for easily integrating Avalara’s RESTful AvaTax API Service. You will need an account with Avalara  (www.avalara.com).

Getting Started
---------------

AvaTax expects a JSON (or XML) POST to their tax/get/ URI, like this:
::
    {
        "DocDate": "2012-10-24",
        "CompanyCode": "FooBar",
        "CustomerCode": "email@email.com",
        "DocCode": "1001",
        "DocType": "SalesOrder",
        "Addresses":
        [
            {
                "AddressCode": "1",
                "Line1": "435 Ericksen Avenue Northeast",
                "Line2": "#250",
                "PostalCode": "98110",
            },
            {
                "AddressCode": "2",
                "Line1": "7562 Kearney St.",
                "PostalCode": "80022-1336",
            },
        ],
        "Lines":
        [
            {
                "LineNo": "1",
                "DestinationCode": "2",
                "OriginCode": "1",
                "Qty": 1,
                "Amount": "100",
            },
        ],
    }

The PyAvaTax API object accepts a Python dictionary that looks just like the above data. We will parse it, validate it, handle the HTTP layer for you, and return an object to you.
::
    api = API(AVALARA_ACCOUNT_NUMBER, AVALARA_LICENSE_KEY, AVALARA_COMPANY_CODE)
    tax_response = api.post_tax(dictionary_data)
    print tax_response.TotalTax

That returned object will have all the response data from AvaTax easily accessible by dot-notation.

Or, an integration using the PyAvaTax library can be done by constructing objects:
::
    api = API(AVALARA_ACCOUNT_NUMBER, AVALARA_LICENSE_KEY, AVALARA_COMPANY_CODE)
    doc = Document.new_sales_order(DocCode='1001', DocDate=datetime.date.today(), CustomerCode='email@email.com')
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
