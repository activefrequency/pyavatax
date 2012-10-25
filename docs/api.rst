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
    :special-members:
    :undoc-members:

Document static factory methods
-------------------------------

The ``new_xxxxx_order`` and ``new_xxxxx_invoice`` calls are static factory functions on the Document class to create a corresponding Document with the intended DocType


Avalara Line
------------

.. autoclass:: Line
    :members:
    :special-members:
    :undoc-members:

Avalara Address
---------------

.. autoclass:: Address
    :members:
    :special-members:
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
    :special-members:
    :undoc-members:

.. currentmodule:: pyavatax.base

.. autoclass:: TaxDetails
    :members:
    :special-members:
    :undoc-members:

.. currentmodule:: pyavatax.api


PostTax Response
----------------

.. autoclass:: PostTaxResponse
    :members:
    :special-members:
    :undoc-members:

.. currentmodule:: pyavatax.base

.. autoclass:: TaxLines
    :members:
    :special-members:
    :undoc-members:

.. autoclass:: TaxDetails
    :members:
    :special-members:
    :undoc-members:

.. autoclass:: TaxAddresses
    :members:
    :special-members:
    :undoc-members:

.. currentmodule:: pyavatax.api


CancelTax Response
------------------

.. autoclass:: CancelTaxResponse
    :members:
    :special-members:
    :undoc-members:

.. currentmodule:: pyavatax.base

.. autoclass:: CancelTaxResult
    :members:
    :special-members:
    :undoc-members:

.. currentmodule:: pyavatax.api


ValidateAddress Response
------------------------

.. autoclass:: ValidateAddressResponse
    :members:
    :special-members:
    :undoc-members:

.. currentmodule:: pyavatax.base

.. autoclass:: Address
    :members:
    :special-members:
    :undoc-members:


Exceptions
==========
.. autoexception:: AvalaraException
    :members:

.. autoexception:: AvalaraServerException
    :members:

.. autoexception:: AvalaraServerDetailException
    :members:
