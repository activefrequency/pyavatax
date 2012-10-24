.. _basics:

The Basics
==========

You can rely on our integration to validate what information you're providing. We also will handle the simple cases of shipping and line numbers, so you don't have to think about Avalara's abstractions and data structures.

Of course, for more complicated interactions all the Avalara flexibility is at your disposal.


Installing the Project
----------------------

If you are using ``pip`` or ``easy_install`` you will find the dependencies of the project in the provided requirements.txt file. Currently the only dependency is the `requests` framework. We use `py.test` for testing, but you don't need to install that to use the library


Instantiating the API
---------------------
Looks like
::
    import avalara
    api = avalara.API(YOUR_ACCOUNT_NUMBER, YOUR_LICENSE_NUMBER, YOUR_COMPANY_CODE, live=True/False)

Once you have an account with Avalara their dashboard page contains the account number and license number. You get to choose a meaningful company code.


Creating a Document
-------------------
Looks like
::
    import avalara
    doc = avalara.Document(**kwargs)
    address = avalara.Address(**kwargs)
    line_item = avalara.Line(**kwargs)

Use the ``kwargs`` parameter to send all the relevant Avalara fields into the document. Any keys that are not Avalara fields will be silently ignored. All the keys **do use Avalara's camel-case notation**.
::
    doc.add_to_address(address)
    doc.add_from_address(another_address)
    doc.add_line(line_item)

For simple shipping cases you can use the helper functions ``add_to_address`` and ``add_from_address``. These will manually add the Avalara ``OriginCode`` and ``DestinationCode`` to the corresponding ``AddressCode``. If your shipping scenario isn't simple, we cannot assume what you're doing - so you will have to input that data onto the objects yourself, like so
::
    address.update({'AddressCode': '3'})
    another_address.update({'AddressCode': '2'})
    a_third_address.update({'AddressCode': '1'})
    line.update({'OriginCode': 1, 'DestinationCode': 3})
    another_line.update({'OriginCode': 2, 'DestinationCode': 3})
    doc.add_address(address)
    doc.add_address(another_address)
    doc.add_address(a_third_address)
    doc.add_line(line)
    doc.add_line(another_line)


Making an API call
------------------
Looks like
::
    response = api.validate_address(address)
    response = api.get_tax(lat=47.627935, lng=-122.51702, doc)
    response = api.post_tax(doc)
    response = api.post_tax(doc, commit=True)

Using the ``commit=True`` on the post_tax call is merely a shortcut for
::
    doc.update({'Commit':True})
    api.post_tax(doc)

You can perform that update logic anywhere and know that ``post_tax`` even without ``commit`` will remain true to the document's state.

Handling a response
-------------------
Looks like
::
    response = api.get_tax(lat=47.627935, lng=-122.51702, doc)
    if response.is_success is True:
        return response.Tax
    else:
        raise ApplicationException(response.error)

The JSON response from Avalara is automatically parsed onto the response object. In the case of a "GetTax" call the attribute 'Tax' is the total taxable amount for your transaction

If the response is not successful, the ``error`` attribute is a list of tuples. The first position is either the offending field (if there is one) or the Avalara class which threw the error. The second position is a human readable description of the error provided by Avalara

Should you need access to the actual response or request the ``response`` attribute is the ``Request`` object which has ``headers``, ``full_url``, ``body``, and other parameters. The ``response`` attribute also has a ``request`` attribute which contains information about the raw request. If you need more details check out their documentation.

Since the ``Request`` library sits on top of the urllib you may not get the **exact data/headers being transmitted**. To account for this I have added a ``proxies`` class variable on the BaseAPI class. It is commented out, but set to the default value for CharlesProxy, an excellent and free GUI application for sniffing the exact data being sent over the wire.

Logging
-------

TODO
