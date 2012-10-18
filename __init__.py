class AvalaraException(Exception):
    pass


class AvalaraServerException(Exception):
    def __init__(self, status_code, response, request_data):
        self.status_code = status_code
        self.response = response
        self.request_data = request_data

    def show_detail(self):
        return "Status: %r \n Response: %r \n Data: %r" % (repr(self.status_code), repr(self.response), repr(self.request_data))

    def __str__(self):
        return "%r" % repr(self.status_code)


# useful for seeing more detail through the tester and logs
# we always throw this exception, though you may catch AvalaraServerException if you don't care
class AvalaraServerDetailException(AvalaraServerException):

    def __str__(self):
        return self.show_detail()
