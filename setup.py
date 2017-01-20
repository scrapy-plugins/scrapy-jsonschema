from setuptools import setup

setup(
    name='scrapy-jsonschema',
    version='0.0.1',
    license='BSD',
    description='Scrapy schema validation pipeline and Item builder using JSON Schema',
    author='Scrapinghub',
    author_email='info@scrapinghub.com',
    url='http://github.com/scrapy-plugins/scrapy-jsonschema',
    packages=['scrapy_jsonschema'],
    platforms=['Any'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    install_requires=['scrapy', 'jsonschema', 'six']
)
