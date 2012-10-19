class AvalaraException(Exception):
    pass


class AvalaraServerException(Exception):
    def __init__(self, response):
        self.status_code = response.status_code
        self.response = response.text
        self.request_data = response.request.data
        self.method = response.request.method
        self.url = response.request.full_url
        self.headers = response.request.headers
        self.params = response.request.params

    def show_detail(self):
        return "Status: %r \n Method: %r, \n URL: %r \n Params: %r \n Headers: %r \n Data: %r \n Response: %r " % (repr(self.status_code), repr(self.method), repr(self.url), repr(self.params), repr(self.headers), repr(self.request_data), repr(self.response))

    def __str__(self):
        return "%r, %r" % (repr(self.status_code), repr(self.url))


# useful for seeing more detail through the tester and logs
# we always throw this exception, though you may catch AvalaraServerException if you don't care
class AvalaraServerDetailException(AvalaraServerException):

    def __str__(self):
        return self.show_detail()
