.. _advanced:

Advanced
========


Running the Tests
-----------------

If you're working with the source code and want to run our tests, you can run the test suite (we are using pytest).

There are some tests specifically for the Django features. If you're not running in a Django environment, those specific tests will return with an expected failure (they will show as ``passed`` because they were expected to fail)

The test script uses a ``settings_local.py`` secrets file that isn't included in this package.  We've included a ``settings_local.py.example`` file that you can copy into ``settings_local.py`` and update with your credentials.

If you have a Django environment you can run ``manage.py shell`` locally and then this:
::
    >>> import pytest
    >>> pytest.main('path/to/pyavatax/test_avalara.py')

Alternatively, you can just do:
::
    $ py.test
