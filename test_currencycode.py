from unittest import TestCase

from pyavatax.base import Document


class TestCurrencyCode(TestCase):

    def test_currency_code_is_set_in_document_object(self):
        currency = 'gbp'
        doc = Document(
            DocType='SalesInvoice',
            CustomerCode='123456789',
            DocCode='12345',
            CompanyCode='COMPANY_CODE',
            CurrencyCode=currency
        )

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

        self.assertIn("CurrencyCode", dictionary.keys())
        self.assertEqual(dictionary.get("CurrencyCode"), currency)
