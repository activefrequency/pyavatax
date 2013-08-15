.. PyAvaTax documentation master file, created by
   sphinx-quickstart on Wed Oct 24 14:35:06 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. _Avalara: http://www.avalara.com
.. _Basics: basics.html
.. _Github: https://github.com/activefrequency/pyavatax/issues

PyAvaTax
=========

What is PyAvaTax?
------------------

As of Sept 2012 US internet retailers are required to pay sales tax in all the states they do business. Avalara_ offers a fully featured web-based service to report your transactions, return your sales tax, and store all the information until you need to report it.

Avalara is a US-only service, and thus all amounts passing through their system, and this api, are assumed to be US Dollars (USD)

We developed PyAvaTax as a Python client library for easily integrating with Avalara's RESTful AvaTax API Service to report your transactions.

PyAvaTax **does not require Django**, though if you are using a Django system we have some admin-based goodies for you to check out! If you're running this on a system with Django installed (e.g. we can find Django in the import path) we will attempt to integrate with it. If you don't want this default behavior, please see the Django section on how to prevent it.

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
    doc.add_from_address(Line1="435 Ericksen Avenue Northeast", Line2="#250", PostalCode="98110")
    doc.add_to_address(Line1="7562 Kearney St.", PostalCode="80022-1336")
    doc.add_line(Amount=10.00)
    response = api.post_tax(doc)


We have a full-fledged introduction, from installation, logging, making requests, and handling responses, with a full example in the next topic: Basics_

If you have any issues, improvements, requests, or bugs please use Github_

Contents:

.. toctree::
   :maxdepth: 2

   basics
   api
   django
   advanced


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

