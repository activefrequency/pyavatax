.. _api:

.. module:: pyavatax.api
.. currentmodule:: pyavatax.api

API Object
===================

.. autoclass:: API
    :members:
    :undoc-members:


.. module:: pyavatax.base
.. currentmodule:: pyavatax.base



Avalara Objects
==============================

Avalara Document
----------------

.. autoclass:: Document
    :members:
    :private-members:
    :undoc-members:

Document static factory methods
-------------------------------

The ``new_xxxxx_order`` and ``new_xxxxx_invoice`` calls are static factory functions on the Document class to create a corresponding Document with the intended DocType


Avalara Line
------------

.. autoclass:: Line
    :members:
    :private-members:
    :undoc-members:

Avalara Address
---------------

.. autoclass:: Address
    :members:
    :private-members:
    :undoc-members:

Avalara TaxOverride
---------------

.. autoclass:: TaxOverride
    :members:
    :private-members:
    :undoc-members:


.. currentmodule:: pyavatax.base

Avalara Response Representations
================================
.. autoclass:: BaseResponse
    :members:

.. autoclass:: ErrorResponse
    :members:

.. currentmodule:: pyavatax.api

GetTax Response
---------------

.. autoclass:: GetTaxResponse
    :members:
    :private-members:
    :undoc-members:

.. currentmodule:: pyavatax.base

.. autoclass:: TaxDetails
    :members:
    :private-members:
    :undoc-members:

.. currentmodule:: pyavatax.api


PostTax Response
----------------

.. autoclass:: PostTaxResponse
    :members:
    :private-members:
    :undoc-members:

.. currentmodule:: pyavatax.base

.. autoclass:: TaxLines
    :members:
    :private-members:
    :undoc-members:

.. autoclass:: TaxDetails
    :members:
    :private-members:
    :undoc-members:

.. autoclass:: TaxAddresses
    :members:
    :private-members:
    :undoc-members:

.. currentmodule:: pyavatax.api


CancelTax Response
------------------

.. autoclass:: CancelTaxResponse
    :members:
    :private-members:
    :undoc-members:

.. currentmodule:: pyavatax.base

.. autoclass:: CancelTaxResult
    :members:
    :private-members:
    :undoc-members:

.. currentmodule:: pyavatax.api


ValidateAddress Response
------------------------

.. autoclass:: ValidateAddressResponse
    :members:
    :private-members:
    :undoc-members:

.. currentmodule:: pyavatax.base

.. autoclass:: Address
    :members:
    :private-members:
    :undoc-members:


Exceptions
==========
.. autoexception:: AvalaraException
    :members:
    :undoc-members:

.. autoexception:: AvalaraTypeException
    :members:

.. autoexception:: AvalaraValidationException
    :members:

.. autoexception:: AvalaraServerException
    :members:

.. autoexception:: AvalaraServerDetailException
    :members:

.. autoexception:: AvalaraServerNotReachableException
    :members:
