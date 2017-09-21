from unittest import TestCase, mock

from pyavatax.api import API
from pyavatax.base import Document


class TestBusinessIdentificationNo(TestCase):

    def test_todict_if_business_identification_no_is_set(self):
        doc = Document(
            DocType='SalesInvoice',
            CustomerCode='123456789',
            DocCode='12345',
            CompanyCode='COMPANY_CODE'
        )

        doc.BusinessIdentificationNo = 'GB999 999'

        doc.add_from_address(
            Line1='000 Main Street',
            City='New York',
            Region='NY',
            Country='US',
            PostalCode='10000'
        )

        doc.add_to_address(
            Line1='001 Main Street',
            Line2='',
            City='New York',
            Region='NY',
            Country='US',
            PostalCode='10000'
        )

        doc.add_line(
            LineNo='1',
            ItemCode='123456789',
            Qty=1,
            Amount=str(100)
        )

        dictionary = doc.todict()

        self.assertIn("BusinessIdentificationNo", dictionary.keys())
        self.assertEqual(dictionary.get("BusinessIdentificationNo"), "GB999 999")
