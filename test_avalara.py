from base import Document, Line
from api import API
import settings_local


def test_gettax():
    api = API(settings_local.AVALARA_ACCOUNT_NUMBER, settings_local.AVALARA_LICENSE_KEY, settings_local.AVALARA_COMPANY_CODE, live=False)
    # A Lat/Long from Avalara's documentation
    lat = 47.627935 
    lng = -122.51702
    line = Line(Amount=10.00)
    doc = Document()
    doc.add_line(line)
    tax = api.get_tax(lat, lng, doc)
    assert tax.is_success() == True
    assert tax.Tax > 0
