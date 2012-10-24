.. _api:

.. module:: avalara.api
.. currentmodule:: avalara.api

Available API Calls
===================

.. autoclass:: API
    :members:

"GetTax"
--------
Performs a HTTP GET to tax/get/

.. automethod:: get_tax


"PostTax" 
---------
Performs a HTTP POST to tax/get/

.. automethod:: post_tax


"CancelTax" 
-----------
Performs a HTTP POST to tax/cancel/

.. automethod:: cancel_tax


"ValidateAddress" 
-----------------
Performs a HTTP GET to address/validate/

.. automethod:: validate_address



.. module:: avalara.base
.. currentmodule:: avalara.base

Avalara Object Representations
==============================

.. autoclass:: Document
    :members:
    :special-members:

.. autoclass:: Line
    :members:
    :special-members:

.. autoclass:: Address
    :members:
    :special-members:

Class methods for creating new documents
----------------------------------------
.. automethod:: new_sales_order
.. automethod:: new_sales_invoice
.. automethod:: new_return_order
.. automethod:: new_return_invoice
.. automethod:: new_purchase_order
.. automethod:: new_purchase_invoice
.. automethod:: new_inventory_order
.. automethod:: new_inventory_invoice

Adding other avalara objects
----------------------------
.. automethod:: add_line
.. automethod:: add_address
.. automethod:: add_to_address
.. automethod:: add_from_address


.. currentmodule:: avalara.base

Avalara Response Representations
================================
.. autoclass:: BaseResponse
    :members:

.. autoclass:: ErrorResponse
    :members:

.. currentmodule:: avalara.api

.. autoclass:: GetTaxResponse
    :members:
    :special-members:

.. currentmodule:: avalara.base

.. autoclass:: TaxDetails
    :members:
    :special-members:

.. currentmodule:: avalara.api

.. autoclass:: PostTaxResponse
    :members:
    :special-members:

.. currentmodule:: avalara.base

.. autoclass:: TaxLines
    :members:
    :special-members:

.. autoclass:: TaxDetails
    :members:
    :special-members:

.. autoclass:: TaxAddresses
    :members:
    :special-members:

.. currentmodule:: avalara.api

.. autoclass:: CancelTaxResponse
    :members:
    :special-members:

.. currentmodule:: avalara.base

.. autoclass:: CancelTaxResult
    :members:
    :special-members:

.. currentmodule:: avalara.api

.. autoclass:: ValidateAddressResponse
    :members:
    :special-members:

.. currentmodule:: avalara.base

.. autoclass:: Address
    :members:
    :special-members:

.. automethod:: describe_address_type
.. automethod:: describe_fips_code
.. automethod:: describe_carrier_route
.. automethod:: describe_post_net


Exceptions
==========
.. autoclass:: AvalaraException
    :members:
    :special-members:

.. autoclass:: AvalaraServerException
    :members:
    :special-members:

.. autoclass:: AvalaraServerDetailException
    :members:
    :special-members:
