=================
scrapy-jsonschema
=================

.. image:: https://travis-ci.org/scrapy-plugins/scrapy-jsonschema.svg?branch=master
    :target: https://travis-ci.org/scrapy-plugins/scrapy-jsonschema

.. image:: https://codecov.io/gh/scrapy-plugins/scrapy-jsonschema/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/scrapy-plugins/scrapy-jsonschema

This plugin provides two features based on `JSON Schema`_ and the
`jsonschema`_ Python library:

* a `Scrapy Item`_ definition builder from a JSON Schema definition
* a `Scrapy item pipeline`_ to validate items against a JSON Schema definition

.. _jsonschema: https://pypi.python.org/pypi/jsonschema
.. _Scrapy Item: https://docs.scrapy.org/en/latest/topics/items.html
.. _Scrapy item pipeline: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


Installation
============

Install scrapy-jsonschema using ``pip``::

    $ pip install scrapy-jsonschema


Configuration
=============

Add ``JsonSchemaValidatePipeline`` by including it in ``ITEM_PIPELINES``
in your ``settings.py`` file::

   ITEM_PIPELINES = {
       ...
       'scrapy_jsonschema.JsonSchemaValidatePipeline': 100,
   }

Here, priority ``100`` is just an example.
Set its value depending on other pipelines you may have enabled already.


Usage
=====

Let's assume that you are working with this JSON schema below,
representing products each requiring a numeric ID, a name, and a non-negative price
(this example is taken from `JSON Schema`_ website)::

    {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "Product",
        "description": "A product from Acme's catalog",
        "type": "object",
        "properties": {
            "id": {
                "description": "The unique identifier for a product",
                "type": "integer"
            },
            "name": {
                "description": "Name of the product",
                "type": "string"
            },
            "price": {
                "type": "number",
                "minimum": 0,
                "exclusiveMinimum": true
            }
        },
        "required": ["id", "name", "price"]
    }

You can define a ``scrapy.Item`` from this schema by subclassing
``scrapy_jsonschema.item.JsonSchemaItem``, and setting a ``jsonschema``
class attribute set to the schema.
This attribute should be a Python ``dict`` -- note that JSON's "true" became ``True`` below;
you can use Python's ``json`` module to load a JSON Schema as string)::

    from scrapy_jsonschema.item import JsonSchemaItem


    class ProductItem(JsonSchemaItem):
        jsonschema =     {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "title": "Product",
            "description": "A product from Acme's catalog",
            "type": "object",
            "properties": {
                "id": {
                    "description": "The unique identifier for a product",
                    "type": "integer"
                },
                "name": {
                    "description": "Name of the product",
                    "type": "string"
                },
                "price": {
                    "type": "number",
                    "minimum": 0,
                    "exclusiveMinimum": true
                }
            },
            "required": ["id", "name", "price"]
        }

You can then use this item class as any regular Scrapy item
(notice how fields that are not in the schema raise errors when assigned)::

    >>> item = ProductItem()
    >>> item['foo'] = 3
    (...)
    KeyError: 'ProductItem does not support field: foo'

    >>> item['name'] = 'Some name'
    >>> item['name']
    'Some name'

If you use this item definition in a spider and if the pipeline is enabled,
generated items that do no follow the schema will be dropped.
In the (unrealistic) example spider below, one of the items only contains the "name",
and "id" and "price" are missing::

    class ExampleSpider(scrapy.Spider):
        name = "example"
        allowed_domains = ["example.com"]
        start_urls = ['http://example.com/']

        def parse(self, response):
            yield ProductItem({
                "name": response.css('title::text').extract_first()
            })

            yield ProductItem({
                "id": 1,
                "name": response.css('title::text').extract_first(),
                "price": 9.99
            })

When running this spider, when the item with missing fields is output,
you should see these lines appear in the logs::

    2017-01-20 12:34:23 [scrapy.core.scraper] WARNING: Dropped: schema validation failed:
     id: 'id' is a required property
    price: 'price' is a required property

    {'name': u'Example Domain'}

The second item conforms to the schema so it appears as a regular item log::

    2017-01-20 12:34:23 [scrapy.core.scraper] DEBUG: Scraped from <200 http://example.com/>
    {'id': 1, 'name': u'Example Domain', 'price': 9.99}


The item pipeline also updates Scrapy stats with a few counters, under
``jsonschema/`` namespace::

    2017-01-20 12:34:23 [scrapy.statscollectors] INFO: Dumping Scrapy stats:
    {...
     'item_dropped_count': 1,
     'item_dropped_reasons_count/DropItem': 1,
     'item_scraped_count': 1,
     'jsonschema/errors/id': 1,
     'jsonschema/errors/price': 1,
     ...}
    2017-01-20 12:34:23 [scrapy.core.engine] INFO: Spider closed (finished)


.. _JSON Schema: http://json-schema.org/
