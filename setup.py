from setuptools import setup

setup(
    name='scrapy-jsonschema',
    version='0.4.0',
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
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    install_requires=['scrapy', 'jsonschema[format]', 'six']
)
