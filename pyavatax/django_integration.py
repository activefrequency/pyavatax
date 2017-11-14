class MockDjangoRecorder(object):

    @staticmethod
    def failure(doc, response):
        pass

    @staticmethod
    def success(doc):
        pass


def get_django_recorder():
    try:
        import django
        from django.utils import timezone
        from django.conf import settings
        from pyavatax.models import AvaTaxRecord
    except ImportError:
        return MockDjangoRecorder
    else:
        if hasattr(settings, 'NO_PYAVATAX_INTEGRATION') and settings.NO_PYAVATAX_INTEGRATION:
            return MockDjangoRecorder
        else:
            class RealDjangoRecorder(object):
                @staticmethod
                def failure(doc, response):
                    AvaTaxRecord.objects.create(doc_code=getattr(doc, 'DocCode', None), failure_details=response._details)

                @staticmethod
                def success(doc):
                    AvaTaxRecord.objects.filter(doc_code=getattr(doc, 'DocCode', None)).update(success_on=timezone.now())
            return RealDjangoRecorder
