from distutils.core import setup
# python setup.py sdist
# python setup.py sdist bdist_wininst upload

version = __import__('pyavatax').get_version()

setup(
    name='PyAvaTax',
    url = 'http://github.com/activefrequency/pyavatax/',
    author = 'John Obelenus',
    author_email = 'jobelenus@activefrequency.com',
    version=version,
    install_requires = ['requests==2.5.3', 'decorator==3.4.0', 'suds-jurko==0.6', 'six==1.9.0'],
    package_data = {
        '': ['*.txt', '*.rst', '*.md']
    },
    packages=['pyavatax',],
    license='BSD',
    long_description="PyAvaTax is a Python library for easily integrating Avalara's RESTful AvaTax API Service",
)
