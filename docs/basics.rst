.. _basics:

The Basics
==========

You can rely on our integration to validate what information you're providing. We handle the simple case of shipping and line numbers, so you don't have to think about AvaTax's abstractions and data structures.

Of course, for more complicated interactions all the AvaTax flexibility is at your disposal.


Installing the Project
----------------------

``pip install pyavatax``

If you are using this project via its source files you will find the dependencies of the project in the provided requirements.txt file. We use `py.test` for testing, but you don't need to install that to use the library.


Instantiating the API
---------------------
Looks like:
::
    import pyavatax
    api = pyavatax.API(YOUR_ACCOUNT_NUMBER, YOUR_LICENSE_NUMBER, YOUR_COMPANY_CODE, live=True/False)

Once you have an account with AvaTax their dashboard page contains the account number and license number. You can choose a meaningful company code.


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
Looks like:
::
    response = api.validate_address(address)
    response = api.get_tax(lat=47.627935, lng=-122.51702, doc)
    # in lieu of making a whole document, you can alternatively pass the amount to be taxed
    response = api.get_tax(lat=47.627935, lng=-122.51702, None, sale_amount=100.00)
    response = api.post_tax(doc)
    response = api.post_tax(doc, commit=True)
    response = api.cancel_tax(doc)

Using the ``commit=True`` on the post_tax call is a shortcut, it is the equivalent of doing this:
::
    doc.update(Commit=True)
    api.post_tax(doc)

However, it will also perform an additional check. Submitting a ``SalesOrder`` (any ``XXXXXOrder``) to AvaTax with ``Commit=True`` won't result in a saved and committed document. It is the wrong type. It needs to be ``SalesInvoice`` ( or ``XXXXXXInvoice``). So if we find an ``XXXXXOrder`` and you pass ``commit=True`` we will automatically update the type for you.

You can perform that update logic anywhere and know that ``post_tax`` even without ``commit`` will remain true to the document's state.

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
    import pyavatax
    doc = pyavatax.Document(**kwargs)
    address = pyavatax.Address(**kwargs)
    line_item = pyavatax.Line(**kwargs)

Use the ``kwargs`` parameter to send all the relevant AvaTax fields into the document. Any keys that are not AvaTax fields will throw an ``AvalaraException``. All the keys **do use AvaTax's camel-case notation**.
::
    doc.add_to_address(address)
    doc.add_from_address(another_address)
    doc.add_line(line_item)

For simple shipping cases you can use the helper functions ``add_to_address`` and ``add_from_address``. These will manually add the AvaTax ``OriginCode`` and ``DestinationCode`` to the corresponding ``AddressCode``. If your shipping scenario isn't simple, we cannot assume what you're doing - so you will have to input that data onto the objects yourself. Here is an exaggerated example to make this use case as clear as possible:
::
    address.update(AddressCode=3)
    another_address.update(AddressCode=2)
    a_third_address.update(AddressCode=1)
    line.update({'OriginCode': 1, 'DestinationCode': 3})
    another_line.update({'OriginCode': 2, 'DestinationCode': 3})
    doc.add_address(address)
    doc.add_address(another_address)
    doc.add_address(a_third_address)
    doc.add_line(line)
    doc.add_line(another_line)



Handling a response
-------------------
Looks like:
::
    response = api.get_tax(lat=47.627935, lng=-122.51702, doc)
    if response.is_success is True:
        return response.Tax
    else:
        raise ApplicationException(response.error)

The JSON response from AvaTax is automatically parsed onto the response object. In the case of a "GetTax" call the attribute 'Tax' is the total taxable amount for your transaction.

If the response is not successful, the ``error`` attribute is a list of tuples. The first item is either the offending field (if there is one) or the AvaTax class which threw the error. The second item is a human readable description of the error provided by AvaTax.

Should you need access to the actual response or request, the ``response`` attribute is the ``Request`` object which has ``headers``, ``full_url``, ``body``, and other parameters. The ``response`` attribute also has a ``request`` attribute which contains information about the raw request. If you need more details check out the AvaTax documentation.

Since the ``Request`` library sits on top of urllib you may not get the **exact data/headers being transmitted**. To account for this you can pass a ``proxies`` dictionary to the ``API`` constructor. You can use this setting to setup Charles Proxy, an excellent and free GUI application for sniffing the exact data being sent over the wire.


Logging
-------

PyAvaTax uses standard Python logging, with a logger called ``pyavatax.api``. All HTTP requests are logged at the ``INFO`` level. All changes that our API makes to your Document objects are logged at the ``DEBUG`` level. All 500 errors, or HTTP Errors (timeouts, unreachable, etc.) are logged to the ``ERROR`` level.

You can pass your own logger, should you so choose, like so:
::
    import pyavatax.AvalaraLogging
    AvalaraLogging.set_logger(my_custom_logger)
    # subsequent api calls will use the custom logger
    response = api.get_tax(lat=47.627935, lng=-122.51702, doc)


