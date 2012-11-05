.. _django:

PyAvaTax features for Django
=============================

If you are integrating PyAvaTax into a django environment you are in luck. In addition to the standard python logging I have implemented a AvaTaxRecord model in this project. If you put `pyavatax` into your installed apps and run `syncdb`, you'll find a new Admin entry.

This way your clients can see which records failed to make it into the Avalara system, since they don't usually have access, or care to access, logs.

You can also get at these records
::
    import pyavatax.models AvaTaxRecord
    AvaTaxRecord.failures.all()

After a Document which has failed runs successfully you'll see if leave that list. And you'll see it popup over here
::
    AvaTaxRecord.successes.all()

Note: if a Document never failed it is never put into either of these lists
