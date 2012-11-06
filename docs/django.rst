.. _django:

PyAvaTax features for Django
============================

If you are integrating PyAvaTax into a Django environment you are in luck. In addition to the standard Python logging I have implemented an AvaTaxRecord model in this project. If you put `pyavatax` into your installed apps and run `syncdb`, you'll find a new Admin entry.

This way your clients can see which records failed to make it into the Avalara system, since they don't usually have access to, or care to access, the logs.

You can also get at these records:
::
    import pyavatax.models AvaTaxRecord
    AvaTaxRecord.failures.all()

After a Document which has failed runs successfully you'll see it leave that list. And you'll see it pop up over here:
::
    AvaTaxRecord.successes.all()

Note: if a Document never failed it is never put into either of these lists.



Your Own Recorder
-----------------

If you want to create your own recorder to perform some special action when a success or failure occurs, the interface looks like this:
::
    class YourSpecialRecorder(object):
        
        @staticmethod
        def failure(doc, response):
            pass

        @staticmethod
        def success(doc):
            pass

To have the API use this recorder just pass the class (or instance, there is no need for them to actually be static methods) as the ``recorder`` keyword-arg to the API instantiation.

Note: ``success`` will always be called in the event of a success, even if a prior failure never occurred.
