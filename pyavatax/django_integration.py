import datetime


def get_django_recorder():
    try:
        import django
        from pyavatax.models import AvaTaxRecord
    except ImportError:
        class MockDjangoRecorder(object):
            
            @staticmethod
            def failure(doc, response):
                pass

            @staticmethod
            def success(doc):
                pass
        return MockDjangoRecorder
    else:
        class RealDjangoRecorder(object):
            @staticmethod
            def failure(doc, response):
                AvaTaxRecord.objects.create(doc_code=getattr(doc, 'DocCode', None), failure_details=response._details)

            @staticmethod
            def success(doc):
                AvaTaxRecord.objects.filter(doc_code=getattr(doc, 'DocCode', None)).update(success_on=datetime.datetime.now())
        return RealDjangoRecorder
