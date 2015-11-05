.. _basics:
.. _short wiki entry: http://en.wikipedia.org/wiki/Pip_(Python)
.. _pypi.org: https://pypi.python.org/pypi
.. _Validate Address: http://developer.avalara.com/api-docs/rest/resources/address-validation
.. _Get Tax: http://developer.avalara.com/api-docs/rest/resources/tax/get
.. _Post Tax: http://developer.avalara.com/api-docs/best-practices/document-lifecycle/posttax-and-committax
.. _Cancel Tax: http://developer.avalara.com/api-docs/rest/resources/tax/cancel
.. _Request and proxies here: http://requests.readthedocs.org/en/latest/user/advanced/#proxies


The Basics
==========

You can rely on our integration to validate what information you're providing. We handle the simple case of shipping and line numbers, so you don't have to think about AvaTax's abstractions and data structures. If you don't add line numbers to your items, we'll add them for you. If you use ``add_to_address`` and ``add_from_address`` you can ignore the ``AddressCode`, ``DestinationCode``, and ``OriginCode`` attributes as well. See the section below about creating a document manually for steps on how to do this.

Of course, for more complicated interactions all the AvaTax flexibility is at your disposal.


Installing the Project
----------------------

If you are using pip (we *highly* recommend using it for managing your Python packages), this is the installation command:

``pip install pyavatax``

If you are using this project via its source files you will find the dependencies of the project in the provided requirements.txt file. We use `py.test` for testing, but you don't need to install that to use the library.

``pip install -r requirements.txt``

If you are unfamiliar with pip/pypi you should check out the `short wiki entry`_ page, and then `pypi.org`_


Copy & Paste
------------

If you're looking for something to copy and paste into your python code base and play with, try this block of code. However, I do ask that you continue to read this basics section (at least) to get a better idea of exactly what is going on.
::

    from pyavatax.api import API
    api = API(YOUR_AVALARA_ACCOUNT_NUMBER, YOUR_AVALARA_LICENSE_KEY, YOUR_AVALARA_COMPANY_CODE, live=False)
    data = {
        "DocDate": "2012-06-13",
        "CompanyCode": YOUR_AVALARA_COMPANY_CODE,
        "CustomerCode": "YourClientsCustomerCode",
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
    try:
        tax = api.post_tax(data)
    except pyavatax.AvalaraServerNotReachableException:
        raise Exception('Avalara is currently down')
    else:  # try else runs whenever there is no exception
        if tax.is_success is True:
            tax.total_tax  # has your total amount of tax for this transaction
        else:
            raise Exception(tax.error)  # Avalara found a problem with your data


Instantiating the API
---------------------
Looks like:
::
    import pyavatax
    api = pyavatax.API(YOUR_ACCOUNT_NUMBER, YOUR_LICENSE_NUMBER, YOUR_COMPANY_CODE, live=True/False)

Once you have an account with AvaTax their dashboard page contains the account number and license number. You can choose a meaningful company code. When live is `False`, the request will be sent to Avalara's test environment. When it is is `True` it will be sent to the production environment.


Creating a Document From Data
-----------------------------
Looks like:
::
    import pyavatax
    doc = Document.from_data(dictionary_data)
    
The ``dictionary_data`` will be validated against the formatting expected by AvaTax. An ``AvalaraException`` will be raised in the cases it does not validate.

For all the API calls you can pass a dictionary, or an object:
::
    doc = Document.from_data(dictionary_data)
    tax = api.post_tax(doc)
    # this line performs the same operation as the above two
    tax = api.post_tax(data_dictionary)


Making an API call
------------------
Here are a few example calls. You can find Avalara's documentation on each of these calls and the parameteres they expect here: `Validate Address`_, `Get Tax`_, `Post Tax`_, `Cancel Tax`_  
::
    response = api.validate_address(address)
    lat = 47.627935
    lng = -122.51702
    response = api.get_tax(lat, lng, doc)
    # in lieu of making a whole document, you can alternatively pass the amount to be taxed
    response = api.get_tax(lat, lng, None, sale_amount=100.00)
    response = api.post_tax(doc)
    response = api.post_tax(doc, commit=True)
    response = api.cancel_tax(doc)

Using the ``commit=True`` on the post_tax call is a shortcut, it is the equivalent of doing this:
::
    doc.update({'Commit': True})
    api.post_tax(doc)

However, it will also perform an additional check. Submitting a ``SalesOrder`` (any ``XXXXXOrder``) to AvaTax with ``Commit=True`` won't result in a saved and committed document. It is the wrong type. It needs to be ``SalesInvoice`` ( or ``XXXXXXInvoice``). So if we find an ``XXXXXOrder`` and you pass ``commit=True`` we will automatically update the type for you.

So far you have noticed we are always using ``SalesOrder`` and ``SalesInvoice`` in our examples. This is for when you are selling products to customers, the most basic example. Other document types are ``ReturnOrder``, ``ReturnInvoice``, ``PurchaseOrder``, ``PurchaseInvoice``, ``InventoryTransferOrder``, and ``InventoryTransferInvoice``. They are used when a customer is returning an item, when you're purchasing items, and when you're transfering inventory.

As an added convenience the response objects from ``post_tax`` and ``get_tax`` have a ``total_tax`` property:
::
    response = api.get_tax(lat=47.627935, lng=-122.51702, doc)
    response.Tax  # is the attribute AvaTax returns
    response.total_tax  # maps to Tax
    response = api.post_tax(doc)
    response.TotalTax  # is the attribute AvaTax returns, note it is not consistent with the other name
    response.total_tax  # maps to TotalTax


Creating a Document Manually
----------------------------
Looks like:
::
    from pyavatax.base import Document, Address, Line
    doc = Document(**kwargs)
    address = Address(**kwargs)
    line_item = Line(**kwargs)

Use the ``kwargs`` parameter to send all the relevant AvaTax fields into the document. Any keys that are not AvaTax fields will throw an ``AvalaraException``. All the keys **do use AvaTax's camel-case notation**.
::
    doc.add_to_address(address)
    doc.add_from_address(another_address)
    doc.add_line(line_item)

For simple shipping cases you can use the helper functions ``add_to_address`` and ``add_from_address``. These will manually add the AvaTax ``OriginCode`` and ``DestinationCode`` to the corresponding ``AddressCode``. If your shipping scenario isn't simple, we cannot assume what you're doing - so you will have to input that data onto the objects yourself. Here is an exaggerated example to make this use case as clear as possible:
::
    address.update({'AddressCode': 3})  # updating address dictionary with address code
    another_address.update({'AddressCode': 2})
    a_third_address.update({'AddressCode': 1})
    line.update({'OriginCode': 1, 'DestinationCode': 3})
    another_line.update({'OriginCode': 2, 'DestinationCode': 3})
    doc.add_address(address)
    doc.add_address(another_address)
    doc.add_address(a_third_address)
    doc.add_line(line)
    doc.add_line(another_line)

Alternatively, if you don't have to have address objects running around for you to modify at a future point before adding to them to a document, you can do it all in one step (like you saw on the documentation index page)
::
    doc.add_from_address(Line1="435 Ericksen Avenue Northeast", Line2="#250", PostalCode="98110")
    doc.add_to_address(**kwargs)




Handling a response
-------------------
Looks like:
::
    try:
        response = api.get_tax(lat=47.627935, lng=-122.51702, doc)
    except AvalaraServerNotReachableException:
        raise ApplicationException('Avalara is currently down')
    else:
        if response.is_success is True:
            return response.Tax
        else:
            raise ApplicationException(response.error)

The JSON response from AvaTax is automatically parsed onto the response object. In the case of a "GetTax" call the attribute 'Tax' is the total taxable amount for your transaction.

If the response is not successful, the ``error`` attribute is a list of tuples. The first item is either the offending field (if there is one) or the AvaTax class which threw the error. The second item is a human readable description of the error provided by AvaTax.

Should you need access to the actual response or request, the ``response`` attribute has the ``Request`` object which has ``headers``, ``full_url``, ``body``, and other parameters. The ``response`` attribute also has a ``request`` attribute which contains information about the raw request. If you need more details check out the AvaTax documentation.

You should use a ``try:  except:`` block to catch ``AvalaraServerNotReachableException`` in the case your network, or Avalara's network has connectivity problems.

Since the ``Request`` library sits on top of urllib you may not get the **exact data/headers being transmitted**. To account for this you can pass a ``proxies`` dictionary to the ``API`` constructor. You can use this setting to setup Charles Proxy, an excellent and free GUI application for sniffing the exact data being sent over the wire. You can see more detail about `Request and proxies here`_: 


Logging
-------

PyAvaTax uses standard Python logging, with a logger called ``pyavatax.api``. All HTTP requests are logged at the ``INFO`` level. All changes that our API makes to your Document objects are logged at the ``DEBUG`` level. All 500 errors, or HTTP Errors (timeouts, unreachable, etc.) are logged to the ``ERROR`` level.

You can pass your own logger, should you so choose, like so:
::
    import pyavatax.base.AvalaraLogging
    AvalaraLogging.set_logger(my_custom_logger)
    # subsequent api calls will use the custom logger
    response = api.get_tax(lat=47.627935, lng=-122.51702, doc)

